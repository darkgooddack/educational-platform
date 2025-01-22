import hashlib
from urllib.parse import urlencode
import secrets
import aiohttp
from fastapi.responses import RedirectResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    OAuthUserSchema,
    TokenSchema,
    UserSchema,
    RegistrationSchema,
    BaseOAuthUserData,
    YandexUserData
)
from app.core.exceptions import (
    InvalidProviderError,
    OAuthInvalidGrantError,
    OAuthTokenError,
    OAuthConfigError,
    OAuthUserCreationError,
    OAuthUserDataError

)
from app.core.config import config
from app.core.clients import RedisClient
from app.core.security import HashingMixin, TokenMixin
from app.models import UserModel
from app.services import (
    BaseService,
    AuthService,
    UserService
)
from app.services.v1.oauth.providers import PROVIDER_HANDLERS
from ..auth import AuthDataManager


class OAuthService(HashingMixin, TokenMixin, BaseService):
    """Сервис для работы с OAuth провайдерами"""

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.providers = config.oauth_providers
        self._auth_service = AuthService(session)
        self._user_service = UserService(session)
        self._data_manager = AuthDataManager(session)

    async def oauthenticate(self, provider: str, code: str) -> TokenSchema:
        """
        Полный процесс OAuth аутентификации

        Args:
            provider: Имя провайдера (vk/google/yandex)
            code: Код, полученный от провайдера

        Returns:
            Токен доступа
        """
        # Получаем токен от провайдера
        token_data = await self._get_provider_token(provider, code)

        self.logger.debug("token_data: %s", token_data)

        # Получаем данные пользователя
        user_data = await self._get_user_info(provider, token_data)

        self.logger.debug("user_data: %s", user_data)

        # Ищем или создаем пользователя
        created_user = await self._get_or_create_user(provider, user_data)

        # Передаем данные созданного пользователя
        self.logger.debug("created_user: %s", created_user)

        return created_user

    async def _get_or_create_user(self, provider: str, user_data: BaseOAuthUserData) -> TokenSchema:
        """
        Аутентифицирует пользователя через OAuth провайдер.

        Args:
            provider: Имя провайдера (vk/google/yandex)
            user_data: Данные пользователя от провайдера

        Returns:
            TokenSchema с access_token
        """

        # Ищем пользователя по provider_id
        provider_field = f"{provider}_id"
        provider_id = str(user_data.id) if provider == "google" else int(user_data.id)

        # Получаем email в зависимости от провайдера
        user_email = (
            user_data.default_email if isinstance(user_data, YandexUserData)
            else user_data.email
        )

        if not user_email:
            self.logger.error("❌ Email не найден в данных пользователя.")
            raise OAuthUserDataError(provider, "Email не найден в данных пользователя")

        self.logger.debug("🔍 Ищем пользователя по провайдеру %s: %s", provider_field, provider_id)

        # Поиск по provider_id
        user_schema = await self._user_service.get_by_field(provider_field, provider_id)

        if user_schema is None:
            self.logger.warning("❌ Пользователь не найден по provider_id, пробуем по email...")

            # Поиск по email
            user_schema = await self._user_service.get_by_email(user_email)

            if user_schema is None:
                self.logger.warning("❌ Пользователь не найден по email, создаем нового пользователя...")

                # Создаем нового пользователя
                oauth_user = OAuthUserSchema(
                    email=user_email,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name,
                    avatar=str(user_data.avatar) if hasattr(user_data, 'avatar') else None,
                    password=secrets.token_hex(16), #! Пароль тогда нужно предлагать поменять или прислать по почте
                    **{provider_field: provider_id}
                )

                self.logger.debug("📝 Создание нового пользователя с email: %s",user_email)
                oauth_user_dict = oauth_user.to_dict()
                registration_data = RegistrationSchema(**oauth_user_dict)

                try:
                    created_user = await self._user_service.create_oauth_user(registration_data)
                    self.logger.debug("✅ Пользователь удачно создан с id: %s",created_user.id)
                except Exception as e:
                    self.logger.error("Ошибка при создании пользователя: %s", e)
                    raise OAuthUserCreationError(provider, str(e)) from e

                # Создаем токен для нового пользователя
                return await self._create_token(created_user)

        # Создаем токен для существующего пользователя
        return await self._auth_service.create_token(user_schema)

    async def _create_token(self, new_user: UserModel) -> TokenSchema:
        """
        Создаем токен для нового пользователя

        Attributes:
            user: Модель пользователя из базы данных после регистрации

        Returns:
            TokenSchema: Токен доступа.

        TODO: Можно переделать получше.
        """
        # Создаем UserSchema для токена
        user_schema = UserSchema(
            id=new_user.id,
            name=new_user.first_name,
            email=new_user.email,
            hashed_password=new_user.hashed_password
        )
        self.logger.debug("🔑 Создание токена для пользователя...")
        # Создаем и возвращаем токен
        return await self._auth_service.create_token(user_schema)

    async def get_oauth_url(self, provider: str) -> RedirectResponse:
        """
        Получение URL для OAuth2 авторизации

        Args:
            provider: Имя провайдера (vk/google/yandex)

        Returns:
            URL для OAuth2 авторизации
        """
        if provider not in self.providers:
            raise InvalidProviderError(provider)

        provider_config = self.providers[provider]
        self._validate_provider_config(provider, provider_config)
        auth_url = await self._build_auth_url(provider, provider_config)

        return RedirectResponse(auth_url)

    def _validate_provider_config(self, provider: str, provider_config: dict) -> None:
        """
        Валидация конфигурации провайдера.
        Проверяет наличие обязательных полей.

        Args:
            provider_config (dict): Конфигурация провайдера

        Raises:
            HTTPException: Если отсутствуют обязательные поля
        """
        required_fields = ["client_id", "client_secret"]
        missing = [field for field in required_fields if field not in provider_config]
        if missing:
            raise OAuthConfigError(provider, missing)

    async def _build_auth_url(self, provider: str, _config: dict) -> str:
        """
        Построение URL для авторизации.

        Args:
            provider (str): Имя провайдера
            provider_config (dict): Конфигурация провайдера

        Returns:
            str: URL для авторизации
        """
        params = {
            "client_id": _config["client_id"],
            "redirect_uri": f"{config.app_url}/api/v1/oauth/{provider}/callback",
            "scope": _config.get("scope", ""),
            "response_type": "code",
        }
        if provider == "vk":
            code_verifier = secrets.token_urlsafe(64)
            code_challenge = hashlib.sha256(code_verifier.encode()).hexdigest()
            params.update({
                "state": secrets.token_urlsafe(32),
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "v": "5.131",
                "display": "page",
                "scope": "email phone",  # Добавляем нужные scope
                "prompt": "",  # Добавляем prompt
                "provider": "vkid",  # Указываем провайдер
                "lang_id": "0",  # Русский язык
                "scheme": "light"  # Светлая тема
            })
            # Сохраняем verifier только для VK
            redis = await RedisClient.get_instance()
            redis.set(f"oauth:verifier:{params['state']}", code_verifier, ex=300)

        return f"{_config['auth_url']}?{urlencode(params)}"

    # Методы работы с провайдерами
    async def _get_provider_token(self, provider: str, code: str) -> dict:
        """
        Получение токена от провайдера.

        Args:
            provider (str): Имя провайдера
            code (str): Код авторизации
        Returns:
            dict: Данные токена
        """
        provider_config = self.providers[provider]

        token_params = {
            "client_id": provider_config["client_id"],
            "client_secret": provider_config["client_secret"],
            "code": code,
            "redirect_uri": f"{config.app_url}/{config.oauth_url}/{provider}/callback",
            "grant_type": "authorization_code",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                provider_config["token_url"],
                data=token_params
            ) as resp:
                token_data = await resp.json()
                if "error" in token_data and token_data["error"] == "invalid_grant":
                    raise OAuthInvalidGrantError(provider)
                elif "error" in token_data:
                    raise OAuthTokenError(provider, token_data["error"])
                return token_data

    async def _get_user_info(self, provider: str, token_data: dict) -> BaseOAuthUserData:
        """
        Получение информации о пользователе от провайдера.

        Args:
            provider (str): Имя провайдера
            token_data (dict): Данные токена
        Returns:
            dict: Информация о пользователе
        """
        provider_config = self.providers[provider]

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}"
            }
            async with session.get(
                provider_config["user_info_url"],
                headers=headers
            ) as resp:
                user_data = await resp.json()

        handler = PROVIDER_HANDLERS.get(provider)
        if not handler:
            raise InvalidProviderError(f"Провайдер {provider} не поддерживается")
        return await handler(user_data)

from urllib.parse import urlencode
import secrets
import aiohttp
from fastapi import HTTPException
from fastapi.responses import RedirectResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import OAuthUserSchema, TokenSchema, UserSchema
from app.core.exceptions import UserNotFoundError, InvalidProviderError, OAuthConfigError
from app.core.config import config
from app.core.security import HashingMixin, TokenMixin
from ..base import BaseService
from .auth import AuthDataManager
from .users import UserService

class OAuthService(HashingMixin, TokenMixin, BaseService):
    """Сервис для работы с OAuth провайдерами"""

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.providers = config.oauth_providers
        self._user_service = UserService(session)
        self._data_manager = AuthDataManager(session)

    async def authenticate(self, provider: str, code: str) -> TokenSchema:
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

        # Получаем данные пользователя
        user_data = await self._get_user_info(provider, token_data)

        # Ищем или создаем пользователя
        user = await self._get_or_create_user(provider, user_data)

        # Генерируем JWT токен
        return await self._create_token(user)

    async def _get_or_create_user(self, provider: str, user_data: dict) -> TokenSchema:
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
        provider_id = str(user_data["id"])

        try:
            # Сначала ищем по provider_id
            return await self._user_service.get_by_field(provider_field, provider_id)
        except UserNotFoundError:
            try:
                # Затем пробуем найти по email
                return await self._user_service.get_by_email(user_data["email"])
            except UserNotFoundError:
                # Базовые поля пользователя
                user_data = {
                    "email": user_data["email"],
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                    "password": secrets.token_hex(16),
                    provider_field: provider_id
                }

                # Создаем пользователя
                oauth_user = OAuthUserSchema(**user_data)
                user = await self._user_service.create_user(oauth_user)
                return await self._user_service.get_by_email(user.email)

    async def _create_token(self, user: UserSchema) -> TokenSchema:
        """
        Создание JWT токена

        Args:
            user: Данные пользователя
        Returns:
            Токен доступа
        """
        payload = self.create_payload(user)
        token = self.generate_token(payload)
        await self._data_manager.save_token(user, token)

        return TokenSchema(access_token=token, token_type=config.token_type)

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
        auth_url = self._build_auth_url(provider, provider_config)

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

    def _build_auth_url(self, provider: str, _config: dict) -> str:
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

                if "error" in token_data:
                    raise HTTPException(
                        status_code=400,
                        detail=token_data["error"]
                    )

    async def _get_user_info(self, provider: str, token_data: dict) -> dict:
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

        return user_data

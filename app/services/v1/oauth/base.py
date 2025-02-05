import logging
import secrets
from abc import ABC, abstractmethod
from urllib.parse import urlencode

from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.exceptions import (OAuthConfigError, OAuthInvalidGrantError,
                                 OAuthTokenError, OAuthUserDataError)
from app.core.http.oauth import OAuthHttpClient
from app.core.security import HashingMixin, TokenMixin
from app.core.storages.redis.oauth import OAuthRedisStorage
from app.schemas import (OAuthConfig, OAuthParams, OAuthProvider,
                         OAuthProviderResponse, OAuthResponse,
                         OAuthTokenParams, OAuthUserData, OAuthUserSchema,
                         RegistrationSchema, UserCredentialsSchema)
from app.services import AuthService
from app.services.v1.users import UserService
from app.services.v1.oauth.handlers import PROVIDER_HANDLERS


class BaseOAuthProvider(ABC, HashingMixin, TokenMixin):
    """
    Базовый класс для OAuth провайдеров.

    Flow аутентификации:
    1. Получение auth_url для редиректа пользователя на провайдера
    2. Получение от провайдера токена по коду аутентификации
    3. Получение от провайдера данных пользователя по токену
    4. Поиск/создание пользователя в базе данных
    5. Генерация токенов для аутентификации пользователя

    Usage:
        # В роутерах:
        @router.get("/oauth/{provider}") # 1
        async def oauth_login(provider: OAuthProvider):
            return await OAuthService(db_session).get_oauth_url(provider) 

        @router.get("/oauth/{provider}/callback") # 2, 3, 4, 5
        async def oauth_callback(provider: OAuthProvider, code: str):
            return await OAuthService(db_session).authenticate(provider, code)
        
        # В сервисе:
        async def get_oauth_url(self, provider: OAuthProvider) -> str:
            oauth_provider = self.get_provider(provider)
            return await oauth_provider.get_auth_url() # 1

        async def authenticate(self, provider: OAuthProvider, code: str) -> OAuthResponse:
            oauth_provider = self.get_provider(provider)
            token = await oauth_provider.get_token(code) # 2
            user_data = await oauth_provider.get_user_info(token["access_token"]) # 3
            return await oauth_provider.authenticate(user_data) # 4, 5
    """

    def __init__(self, provider: OAuthProvider, session: AsyncSession):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.provider = provider
        self.config = OAuthConfig(**config.oauth_providers[provider])
        self.user_handler = PROVIDER_HANDLERS[provider]
        self._auth_service = AuthService(session)
        self._user_service = UserService(session)
        self._redis_storage = OAuthRedisStorage()
        self.http_client = OAuthHttpClient()

    async def authenticate(self, user_data: OAuthUserData) -> OAuthResponse:
        """
        Аутентификация через OAuth провайдер.

        Flow:
        1. Поиск пользователя по provider_id
        2. Если не найден - поиск по email
        3. Если не найден - создание нового пользователя
        4. Генерация токенов

        Args:
            user_data: Данные пользователя от провайдера

        Returns:
            OAuthResponse: Токены и redirect_uri

        Usage:
            # В провайдере
            token_data = await self.get_token(code)
            user_data = await self.get_user_info(token_data.access_token)
            return await self.authenticate(user_data)
        """
        user = await self._find_user(user_data)
        if not user:
            user = await self._create_user(user_data)
        return await self._create_tokens(user)

    async def _find_user(
        self, user_data: OAuthUserData
    ) -> UserCredentialsSchema | None:
        """
        Поиск существующего пользователя по данным OAuth.

        Порядок поиска:
        1. По ID провайдера ({provider}_id)
        2. По email пользователя

        Args:
            user_data: Данные пользователя от OAuth провайдера

        Returns:
            UserCredentialsSchema | None: Найденный пользователь или None

        Usage:
            user = await self._find_user(oauth_data)
            if not user:
                user = await self._create_user(oauth_data)
        """
        provider_id = self._get_provider_id(user_data)
        user = await self._user_service.get_user_by_field(
            f"{self.provider}_id", provider_id
        )
        if not user:
            user = await self._user_service.get_user_by_email(
                self._get_email(user_data)
            )
        return user

    def _get_provider_id(self, user_data: OAuthUserData) -> int:
        """
        Получение ID пользователя от провайдера.

        Args:
            user_data: Данные пользователя от провайдера

        Returns:
            ID пользователя в числовом формате

        Usage:
            # Базовая реализация для VK, Yandex
            provider_id = self._get_provider_id(user_data)  # Returns: 12345

            # Google провайдер
            def _get_provider_id(self, user_data: OAuthUserData) -> str:
                return str(user_data.id)  # Returns: "12345"
        """
        return int(user_data.id)

    def _get_email(self, user_data: OAuthUserData) -> str:
        """
        Получение email пользователя.

        Args:
            user_data: Данные пользователя от провайдера

        Returns:
            Email пользователя

        Raises:
            OAuthUserDataError: Если email не найден

        Usage:
            # Базовая реализация для Google
            email = self._get_email(user_data)  # Returns: user@gmail.com

            # VK провайдер
            def _get_email(self, user_data: VKUserData) -> str:
                if not user_data.email:
                    raise OAuthUserDataError(self.provider, "VK не предоставил  email")
                return user_data.email

            # Yandex провайдер
            def _get_email(self, user_data: YandexUserData) -> str:
                return user_data.default_email
        """
        if not user_data.email:
            raise OAuthUserDataError(
                self.provider, "Email не найден в данных пользователя"
            )
        return user_data.email

    async def _create_user(self, user_data: OAuthUserData) -> UserCredentialsSchema:
        """
        Создание нового пользователя через OAuth.

        Процесс создания:
        1. Формирование данных пользователя из OAuth профиля
        2. Создание пользователя в БД
        3. Преобразование в схему для токена

        Args:
            user_data: Данные пользователя от OAuth провайдера

        Returns:
            UserCredentialsSchema: Схема пользователя для создания токена

        Usage:
            oauth_data = await provider.get_user_info(token)
            user = await self._create_user(oauth_data)
            # Returns: UserCredentialsSchema(id=1, email="user@mail.com", name="John")

        Notes:
            - Если first_name не указан, берется часть email до @
            - Пароль генерируется случайным образом
            - ID провайдера сохраняется в поле {provider}_id
        """

        oauth_user = OAuthUserSchema(
            email=self._get_email(user_data),
            first_name=user_data.first_name or self._get_email(user_data).split("@")[0],
            last_name=user_data.last_name,
            avatar=getattr(user_data, "avatar", None),
            password=secrets.token_hex(16),
            **{f"{self.provider}_id": self._get_provider_id(user_data)},
        )

        user_credentials = await self._user_service.create_oauth_user(
            RegistrationSchema(**oauth_user.model_dump())
        )

        self.logger.debug("Созданный пользователь (user_credentials): %s", vars(user_credentials))

        return user_credentials

    async def _create_tokens(self, user: UserCredentialsSchema) -> OAuthResponse:
        """
        Генерация access и refresh токенов для OAuth аутентификации.

        Flow:
        1. Создание access токена через AuthService
        2. Генерация refresh токена
        3. Формирование ответа с redirect_uri

        Args:
            user: Схема пользователя для создания токенов

        Returns:
            OAuthResponse: Токены и URI для редиректа

        Usage:
            tokens = await self._create_tokens(user_schema)
            # Returns: OAuthResponse(
            #    access_token="eyJ...",
            #    refresh_token="eyJ...",
            #    redirect_uri="/home"
            # )
        """
        access_token = await self._auth_service.create_token(user)
        refresh_token = TokenMixin.generate_token(
            {
                "sub": user.email,
                "type": "refresh",
                "expires_at": TokenMixin.get_token_expiration(),
            }
        )
        return OAuthResponse(
            **access_token.model_dump(),
            refresh_token=refresh_token,
            redirect_uri=config.oauth_success_redirect_uri,
        )

    def _validate_config(self) -> None:
        """
        Валидация конфигурации провайдера

        Проверяет наличие обязательных полей в конфигурации провайдера:
            - client_id
            - client_secret

        Данные параметрые необходимо получить у провайдера и хранить в секретах.

        Если какое-то из полей не указано, выбрасывается исключение OAuthConfigError
        """
        if not self.config.client_id or not self.config.client_secret:
            raise OAuthConfigError(self.provider, ["client_id", "client_secret"])

    @abstractmethod
    async def get_auth_url(self) -> RedirectResponse:
        """
        Получение URL для OAuth авторизации.

        #! Этот метод должен быть реализован в каждом наследуемом классе.

        Базовая реализация:
        1. Валидирует конфигурацию провайдера
        2. Формирует базовые OAuth параметры
        3. Строит URL для авторизации

        Специальные механизмы авторизации:
        - VK: Использует PKCE (code_verifier + code_challenge)
            code_verifier = secrets.token_urlsafe(64)
            code_challenge = base64(sha256(code_verifier))
            params = VKOAuthParams(code_challenge=code_challenge)

        Usage:
            @router.get("/oauth/{provider}")
            async def oauth_login(provider: str):
                return await oauth_provider.get_auth_url()

            # VK Provider
            async def get_auth_url(self):
                params = VKOAuthParams(
                    code_challenge=self._generate_code_challenge(),
                    state=secrets.token_urlsafe()
                )
                await self._redis_storage.save_verifier(params.state, code_verifier)
                return RedirectResponse(url=f"{self.auth_url}?{urlencode(params)}")

            # Генерация кода challenge для OAuth2 (используется для VK).
            def _generate_code_challenge(self, verifier: str) -> str:
                return base64.urlsafe_b64encode(
                    hashlib.sha256(verifier.encode()).digest()
                ).decode().rstrip('=')

        Returns:
            RedirectResponse: Редирект на URL авторизации провайдера
        """
        self._validate_config()

        params = OAuthParams(
            client_id=self.config.client_id,
            redirect_uri=await self._get_callback_url(),
            scope=self.config.scope,
        )

        auth_url = f"{self.config.auth_url}?{urlencode(params.model_dump())}"
        return RedirectResponse(url=auth_url)

    @abstractmethod
    async def get_token(self, code: str, state: str = None) -> OAuthProviderResponse:
        """
        Получение токена доступа от OAuth провайдера.

        #! Этот метод должен быть реализован в каждом наследуемом классе.

        Flow:
        1. Формирование параметров запроса
        2. Обработка state параметра если требуется
        3. Отправка запроса на получение токена
        4. Обработка ошибок

        Args:
            code: Код авторизации от провайдера
            state: Параметр state для безопасности (опционально)

        Returns:
            OAuthProviderResponse: Токен доступа и связанные данные

        Raises:
            OAuthInvalidGrantError: Если код авторизации невалиден
            OAuthTokenError: При других ошибках получения токена

        Usage:
            token_data = await provider.get_token(code, state)
            user_info = await provider.get_user_info(token_data.access_token)
        """

        token_params = OAuthTokenParams(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            code=code,
            redirect_uri=str(await self._get_callback_url()),
        )

        if hasattr(self, "_handle_state"):
            self.logger.debug("Начало работы с handle_state:")
            self.logger.debug(f"state: {state}")
            self.logger.debug(f"token_params: {token_params.model_dump()}")
            await self._handle_state(state, token_params.model_dump())

        token_data = await self.http_client.get_token(
            self.config.token_url, 
            token_params.model_dump()
        )

        if "error" in token_data:
            if token_data["error"] == "invalid_grant":
                raise OAuthInvalidGrantError(self.provider)
            raise OAuthTokenError(self.provider, token_data["error"])

        return token_data

    @abstractmethod
    async def get_user_info(self, token: str) -> OAuthUserData:
        """
        Получение данных пользователя от OAuth провайдера.

        #! Этот метод должен быть реализован в каждом наследуемом классе.

        Flow:
        1. Запрос к API провайдера с токеном
        2. Преобразование ответа в единый формат через handler

        Args:
            token: Токен доступа от провайдера

        Returns:
            OAuthUserData: Унифицированные данные пользователя

        Usage:
            # В базовом провайдере
            user_data = await self.http_client.get_user_info(
                self.config.user_info_url,
                token
            )
            return await self.user_handler(user_data)

            # В конкретном провайдере
            async def get_user_info(self, token: str) -> OAuthUserData:
                data = await super().get_user_info(token)
                # Дополнительная обработка если нужно
                return data
        """
        user_data = await self.http_client.get_user_info(
            self.config.user_info_url, token
        )
        return await self.user_handler(user_data)

    @abstractmethod
    async def _get_callback_url(self) -> str:
        """
        Генерирует callback URL для OAuth провайдера.

        #! Этот метод должен быть реализован в каждом наследуемом классе.

        Этот метод использует конфигурацию приложения для формирования полного URL,
        который включает в себя текущий домен, версию API и имя провайдера.

        Пример использования:
            url = await provider._get_callback_url()
            # Возвращает: https://domain.com/api/v1/oauth/google/callback

        Returns:
            str: Полный валидный URL для callback эндпоинта провайдера.
        """
        return self.config.callback_url.format(provider=self.provider)

    @abstractmethod
    async def _handle_state(self, state: str, token_params: dict) -> None:
        """
        Обработка state параметра для OAuth провайдера.

        #! Этот метод должен быть реализован в каждом наследуемом классе.

        Метод реализует различные механизмы безопасности OAuth flow:
        - VK: PKCE (Proof Key for Code Exchange) с code_verifier
        - Google: Защита от CSRF атак через state
        - Yandex: Не использует state

        Args:
            state: Параметр state из OAuth callback
            token_params: Параметры для получения токена

        Usage:
            # VK Provider
            async def _handle_state(self, state: str, token_params: dict) -> None:
                if state:
                    verifier = await self._redis_storage.get_verifier(state)
                    if not verifier:
                        raise OAuthTokenError(self.provider, "Invalid state/    verifier")
                    token_params["code_verifier"] = verifier
                    await self._redis_storage.delete_verifier(state)

            # Google Provider
            async def _handle_state(self, state: str, token_params: dict) -> None:
                if state != await self._redis_storage.get_state():
                    raise OAuthTokenError(self.provider, "Invalid state")
        """
        pass

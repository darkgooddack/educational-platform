import secrets
from urllib.parse import urlencode

from fastapi.responses import RedirectResponse

from app.core.exceptions import OAuthTokenError
from app.schemas import (GoogleTokenData, GoogleUserData, OAuthParams,
                         OAuthProvider, OAuthProviderResponse)
from app.services.v1.oauth.base import BaseOAuthProvider


class GoogleOAuthProvider(BaseOAuthProvider):
    """
    OAuth провайдер для Google.

    Особенности:
    - Использует строковый формат ID пользователя
    - Поддерживает OpenID Connect (id_token)
    - Стандартный OAuth2 flow с state для CSRF защиты

    Flow:
    1. Получение auth_url с state параметром
    2. Редирект пользователя на страницу входа Google
    3. Получение code и state от Google
    4. Обмен code на access_token и id_token
    5. Получение данных пользователя через access_token
    """

    def __init__(self, session):
        """
        Инициализация Google OAuth провайдера.

        Args:
            session: Сессия базы данных
        """
        super().__init__(provider=OAuthProvider.GOOGLE.value, session=session)

    async def get_auth_url(self) -> RedirectResponse:
        """
        Формирование URL для OAuth авторизации через Google.

        Генерирует случайный state для CSRF защиты и сохраняет в Redis.
        Добавляет необходимые OAuth параметры в URL.

        Returns:
            RedirectResponse: URL для перенаправления на страницу входа Google
        """
        state = secrets.token_urlsafe()
        await self._redis_storage.set(f"google_state_{state}", state)

        params = OAuthParams(
            client_id=self.config.client_id,
            redirect_uri=await self._get_callback_url(),
            scope=self.config.scope,
            state=state,
        )

        auth_url = f"{self.config.auth_url}?{urlencode(params.model_dump())}"
        return RedirectResponse(url=auth_url)

    async def get_token(
        self, code: str, state: str = None, device_id: str = None
    ) -> GoogleTokenData:
        """
        Получение токена от Google по коду авторизации.

        Проверяет наличие кода и обменивает его на access_token и id_token.
        Поддерживает OpenID Connect flow.

        Args:
            code: Код авторизации от Google
            state: Параметр state для проверки CSRF
            device_id: Не используется

        Returns:
            GoogleTokenData: Токен доступа и связанные данные

        Raises:
            OAuthTokenError: При отсутствии кода или ошибке от Google API
        """

        if not code:
            raise OAuthTokenError(self.provider, "Не передан код авторизации")

        token_data = await self._get_token_data(code, state)
        return GoogleTokenData(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "bearer"),
            expires_in=token_data["expires_in"],
            id_token=token_data["id_token"],
            scope=token_data["scope"],
        )

    async def get_user_info(self, token: str) -> GoogleUserData:
        """
        Получение данных пользователя через Google API.

        Использует стандартный эндпоинт Google для получения
        информации о пользователе. Возвращает данные в формате GoogleUserData.

        Args:
            token: Токен доступа от Google

        Returns:
            GoogleUserData: Данные пользователя в унифицированном формате
        """
        return await super().get_user_info(token)

    def _get_provider_id(self, user_data: GoogleUserData) -> str:
        """
        Преобразование ID пользователя в строковый формат.
        Google всегда возвращает строковый ID.
        """
        return str(user_data.id)

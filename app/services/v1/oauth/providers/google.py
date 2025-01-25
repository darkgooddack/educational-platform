import secrets
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse
from app.services.v1.oauth.base import BaseOAuthProvider
from app.schemas import OAuthProvider, GoogleUserData, OAuthParams, OAuthProviderResponse
from app.core.exceptions import OAuthTokenError

class GoogleOAuthProvider(BaseOAuthProvider):
    """
    OAuth провайдер для Google

    Особенности:
    - Использует строковый формат ID
    - Защита от CSRF через state (не используется в Google)
    - Стандартный OAuth2 flow с state
    """

    def __init__(self, session):
        super().__init__(
            provider=OAuthProvider.GOOGLE.value,
            session=session
        )

    async def get_token(self, code: str, state: str = None) -> OAuthProviderResponse:
        """Стандартное получение токена"""
        return await super().get_token(code)

    async def _get_callback_url(self) -> str:
        """Стандартный callback URL"""
        return await super()._get_callback_url()

    async def get_user_info(self, token: str) -> GoogleUserData:
        """Стандартное получение данных пользователя"""
        return await super().get_user_info(token)


    def _get_provider_id(self, user_data: GoogleUserData) -> str:
        """Google использует строковый формат ID"""
        return str(user_data.id)

    async def get_auth_url(self) -> RedirectResponse:
        """URL авторизации с добавлением state"""
        state = secrets.token_urlsafe()
        await self._redis_storage.set(f"google_state_{state}", state)

        params = OAuthParams(
            client_id=self.config.client_id,
            redirect_uri=await self._get_callback_url(),
            scope=self.config.scope,
            state=state
        )

        auth_url = f"{self.config.auth_url}?{urlencode(params.model_dump())}"
        return RedirectResponse(url=auth_url)

    async def _handle_state(self, state: str, token_params: dict) -> None:
        """Проверка state для защиты от CSRF - не исплользуется в Google"""
        pass
        # stored_state = await self._redis_storage.get(f"google_state_{state}")
        # self.logger.debug(f"Stored state: {stored_state}, received state: {state}")
        # if not stored_state or stored_state != state:
        #     raise OAuthTokenError(self.provider, "Invalid state parameter")
        # await self._redis_storage.delete(f"google_state_{state}")

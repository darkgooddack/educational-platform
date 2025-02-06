from fastapi.responses import RedirectResponse

from app.core.exceptions import OAuthUserDataError
from app.schemas import OAuthProvider, OAuthProviderResponse, YandexUserData, YandexTokenData
from app.services.v1.oauth.base import BaseOAuthProvider


class YandexOAuthProvider(BaseOAuthProvider):
    """
    OAuth провайдер для Яндекса

    Особенности:
    - Использует default_email вместо email
    - Не использует state параметр
    - Стандартный OAuth2 flow
    """

    def __init__(self, session):
        super().__init__(provider=OAuthProvider.YANDEX.value, session=session)

    def _get_email(self, user_data: YandexUserData) -> str:
        """Получение email из default_email
        Yandex может не предоставить email если пользователь не был зарегистрирован
        """
        if not user_data.email:
            raise OAuthUserDataError(self.provider, "Yandex не предоставил email")
        return user_data.default_email

    async def get_auth_url(self) -> RedirectResponse:
        """Стандартный URL авторизации"""
        return await super().get_auth_url()

    async def get_token(self, code: str, state: str = None, device_id: str = None) -> OAuthProviderResponse:
        """Стандартное получение токена"""
        token_data = await self._get_token_data(code, state)
        return YandexTokenData(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "bearer"),
            expires_in=token_data["expires_in"],
            refresh_token=token_data["refresh_token"],
            scope=token_data["scope"]
        )

    async def get_user_info(self, token: str) -> YandexUserData:
        """Стандартное получение данных пользователя"""
        return await super().get_user_info(token)

    async def _get_callback_url(self) -> str:
        """Стандартный callback URL"""
        return await super()._get_callback_url()

    async def _handle_state(self, state: str, token_params: dict) -> None:
        """Яндекс не использует state"""
        pass

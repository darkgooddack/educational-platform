from fastapi.responses import RedirectResponse

from app.core.exceptions import OAuthUserDataError
from app.schemas import OAuthProvider, OAuthProviderResponse, YandexUserData
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

    async def get_token(self, code: str, state: str = None) -> OAuthProviderResponse:
        """Стандартное получение токена"""
        return await super().get_token(code)

    async def get_user_info(self, token: str) -> YandexUserData:
        """Стандартное получение данных пользователя"""
        return await super().get_user_info(token)

    async def _get_callback_url(self) -> str:
        """Стандартный callback URL"""
        return await super()._get_callback_url()

    async def _handle_state(self, state: str, token_params: dict) -> None:
        """Яндекс не использует state"""
        pass

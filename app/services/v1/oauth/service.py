import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.v1.oauth.oauth import OAuthProvider, OAuthResponse
from app.services.v1.oauth.providers import (
    YandexOAuthProvider,
    GoogleOAuthProvider,
    VKOAuthProvider
)
logging.basicConfig(level=logging.DEBUG)
class OAuthService:
    """
    Сервис для работы с OAuth провайдерами.

    Предоставляет:
    - Получение провайдера по типу
    - Обработку OAuth авторизации
    - Получение URL авторизации
    """

    PROVIDERS = {
        OAuthProvider.YANDEX: YandexOAuthProvider,
        OAuthProvider.GOOGLE: GoogleOAuthProvider,
        OAuthProvider.VK: VKOAuthProvider
    }

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_provider(self, provider: OAuthProvider):
        """Получение инстанса провайдера"""
        provider_class = self.PROVIDERS[provider]
        return provider_class(self.session)

    async def get_oauth_url(self, provider: OAuthProvider):
        """Получение URL для OAuth авторизации"""
        oauth_provider = self.get_provider(provider)
        return await oauth_provider.get_auth_url()

    async def authenticate(self, provider: OAuthProvider, code: str) -> OAuthResponse:
        """Аутентификация через OAuth"""
        oauth_provider = self.get_provider(provider)
        self.logger.debug(f"Authenticating with {provider} using code {code}")
        token = await oauth_provider.get_token(code)
        self.logger.debug(f"Token received: {token}")
        user_data = await oauth_provider.get_user_info(token["access_token"])
        self.logger.debug(f"User data received: {user_data}")
        return await oauth_provider.authenticate(user_data)

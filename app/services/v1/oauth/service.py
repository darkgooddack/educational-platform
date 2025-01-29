import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.v1.oauth.oauth import OAuthProvider, OAuthResponse
from app.services.v1.oauth.providers import (GoogleOAuthProvider,
                                             VKOAuthProvider,
                                             YandexOAuthProvider)

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
        OAuthProvider.VK: VKOAuthProvider,
    }

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_provider(self, provider: OAuthProvider):
        """
        Получение инстанса провайдера

        Args:
            provider: OAuthProvider

        Returns:
            BaseOAuthProvider: Инстанс провайдера
        """
        provider_class = self.PROVIDERS[provider]
        return provider_class(self.session)

    async def get_oauth_url(self, provider: OAuthProvider) -> str:
        """
        Получение URL для OAuth авторизации

        Args:
            provider: OAuthProvider

        Returns:
            str: URL для OAuth авторизации
        """
        oauth_provider = self.get_provider(provider)
        return await oauth_provider.get_auth_url()

    async def authenticate(self, provider: OAuthProvider, code: str) -> OAuthResponse:
        """
        Аутентификация через OAuth

        Flow:
        1. Получение токена по коду авторизации (get_token)
        2. Получение данных пользователя по токену (get_user_info)
        3. Аутентификация и выдача токенов (authenticate)

        Args:
            provider: OAuthProvider
            code: Код авторизации

        Returns:
            OAuthResponse: Токены и данные пользователя
        """
        oauth_provider = self.get_provider(provider)

        token = await oauth_provider.get_token(code) #! state не передается, он равен None

        user_data = await oauth_provider.get_user_info(token["access_token"])

        return await oauth_provider.authenticate(user_data)

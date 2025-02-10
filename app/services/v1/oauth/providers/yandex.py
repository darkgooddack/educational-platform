from fastapi.responses import RedirectResponse

from app.core.exceptions import OAuthUserDataError, OAuthTokenError
from app.schemas import (OAuthProvider, OAuthProviderResponse, YandexTokenData,
                         YandexUserData)
from app.services.v1.oauth.base import BaseOAuthProvider


class YandexOAuthProvider(BaseOAuthProvider):
    """
    OAuth провайдер для Яндекса.

    Реализует стандартный OAuth2 flow для Яндекс ID:
    1. Редирект на страницу авторизации Яндекса
    2. Получение токена по коду авторизации
    3. Получение данных пользователя через Яндекс API

    Особенности:
    - Использует default_email вместо обычного email
    - Не использует state параметр для CSRF защиты
    - Возвращает refresh_token для обновления доступа
    - Требует scope с доступом к email

    Attributes:
        provider (str): Идентификатор провайдера ("yandex")
        config (OAuthConfig): Конфигурация из настроек приложения
        user_handler (Callable): Обработчик данных пользователя

    Usage:
        provider = YandexOAuthProvider(session)

        # 1. Получение URL для авторизации
        auth_url = await provider.get_auth_url()

        # 2. Получение токена по коду
        token = await provider.get_token(code)

        # 3. Получение данных пользователя
        user_data = await provider.get_user_info(token.access_token)
    """

    def __init__(self, session):
        """
        Инициализация Яндекс OAuth провайдера.

        Args:
            session: Сессия базы данных
        """
        super().__init__(provider=OAuthProvider.YANDEX.value, session=session)

    def _get_email(self, user_data: YandexUserData) -> str:
        """
        Получение email пользователя из default_email.

        Яндекс возвращает основной email в поле default_email,
        который используется для идентификации пользователя.

        Args:
            user_data: Данные пользователя от Яндекса

        Returns:
            str: Email пользователя

        Raises:
            OAuthUserDataError: Если email отсутствует в данных
        """
        if not user_data.email:
            raise OAuthUserDataError(self.provider, "Yandex не предоставил email")
        return user_data.default_email

    async def get_auth_url(self) -> RedirectResponse:
        """
        Формирование URL для OAuth авторизации через Яндекс.

        Использует стандартный OAuth2 flow без дополнительных параметров.
        Не требует state для CSRF защиты.

        Returns:
            RedirectResponse: URL для перенаправления на страницу входа Яндекс
        """
        return await super().get_auth_url()

    async def get_token(
        self, code: str, state: str = None, device_id: str = None
    ) -> OAuthProviderResponse:
        """
        Получение токена доступа от Яндекса.

        Args:
            code: Код авторизации
            state: Не используется
            device_id: Не используется

        Returns:
            YandexTokenData: Токен доступа и refresh токен

        Raises:
            OAuthTokenError: При отсутствии кода или ошибке от API
        """
        if not code:
            raise OAuthTokenError(self.provider, "Не передан код авторизации")

        token_data = await self._get_token_data(code, state)
        return YandexTokenData(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "bearer"),
            expires_in=token_data["expires_in"],
            refresh_token=token_data["refresh_token"],
            scope=token_data["scope"],
        )

    async def get_user_info(self, token: str) -> YandexUserData:
        """
        Получение данных пользователя через Яндекс API.

        Использует стандартный эндпоинт Яндекс ID для получения
        информации о пользователе. Возвращает данные в формате YandexUserData.

        Args:
            token: Токен доступа от Яндекса

        Returns:
            YandexUserData: Данные пользователя в унифицированном формате
        """
        return await super().get_user_info(token)

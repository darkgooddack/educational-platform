import secrets
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.v1.auth.auth import TokenSchema
from app.schemas.v1.auth.register import RegistrationSchema

from ..base import BaseInputSchema, CommonBaseSchema


class OAuthProvider(str, Enum):
    """
    Наименования поддерживаемых OAuth провайдеры

    Чтобы получить, необходимо использовать .value например:
    OAuthProvider.YANDEX.value

    Пример использования:
    OAuthProvider.YANDEX.value == "yandex"

    """

    YANDEX = "yandex"
    GOOGLE = "google"
    VK = "vk"


class OAuthConfig(CommonBaseSchema):
    """
    Конфигурация OAuth провайдера

    Attributes:
        client_id: Идентификатор приложения
        client_secret: Секретный ключ приложения
        auth_url: URL для авторизации
        token_url: URL для получения токена
        user_info_url: URL для получения информации о пользователе
        scope: Область доступа
        callback_url: URL для перенаправления после авторизации (для провайдера)
    """

    client_id: str | int # VK: client_id = id приложения >_<
    client_secret: str
    auth_url: str
    token_url: str
    user_info_url: str
    scope: str
    callback_url: str


class OAuthParams(BaseModel):
    """
    Базовый класс для OAuth параметров

    Attributes:
        client_id: Идентификатор приложения
        redirect_uri: Путь для перенаправления после авторизации (для пользователя)
        scope: Область доступа
        response_type: Тип ответа (code)
    """

    client_id: str | int # VK: client_id = id приложения >_<
    redirect_uri: str
    scope: str = ""
    response_type: str = "code"


class VKOAuthParams(OAuthParams):
    """
    Класс для дополнительных параметров OAuth авторизации через VK
    """

    state: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    code_challenge: str
    code_challenge_method: str = "S256"


class OAuthResponse(TokenSchema):
    """
    Схема ответа OAuth авторизации.

    Attributes:
        access_token: Токен доступа
        token_type: Тип токена (bearer)
        refresh_token: Токен обновления токена
        redirect_uri: Путь для перенаправления после авторизации (для пользователя)
    """

    refresh_token: str | None = None
    redirect_uri: str = "/"


class OAuthUserData(CommonBaseSchema):
    """
    Базовый класс для данных пользователя OAuth

    Attributes:
        id: Идентификатор пользователя
        email: Электронная почта пользователя
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        avatar: Ссылка на аватар пользователя
    """

    id: str
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: Optional[str] = None


class YandexUserData(OAuthUserData):
    """
    Класс для данных пользователя OAuth через Яндекс

    Attributes:
        default_email: Основная электронная почта пользователя в Яндекс ID (у других обычно email)
        login: Логин пользователя
        emails: Список электронных почт пользователя
        psuid: Идентификатор пользователя в Яндекс ID
    """

    default_email: EmailStr
    login: str | None = None
    emails: list[EmailStr] | None = None
    psuid: str | None = None


class GoogleUserData(OAuthUserData):
    """
    Класс для данных пользователя OAuth через Google

    Attributes:
        email_verified: Флаг, указывающий, что электронная почта пользователя была подтверждена
        given_name: Имя пользователя
        family_name: Фамилия пользователя
        picture: Ссылка на аватар пользователя
    """

    verified_email: bool = False
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None


class VKUserData(OAuthUserData):
    """
    Класс для данных пользователя OAuth через VK

    Attributes:
        phone: Номер телефона пользователя
        user_id: Идентификатор пользователя
    """

    phone: str | None = None
    user_id: str | None = None


class OAuthTokenParams(CommonBaseSchema):
    """
    Класс для параметров OAuth авторизации (для получения токена)

    Attributes:
        client_id: Идентификатор приложения
        client_secret: Секретное слово приложения
        code: Код авторизации
        redirect_uri: Путь для перенаправления после авторизации (для провайдера)
    """

    client_id: str | int
    client_secret: str
    code: str
    redirect_uri: str
    grant_type: str = "authorization_code"

class VKOAuthTokenParams(OAuthTokenParams):
    """
    Параметры для получения токена VK OAuth

    Attributes:
        client_id: ID приложения VK
        client_secret: Секретный ключ приложения
        code: Код авторизации
        redirect_uri: URL для callback
        grant_type: Тип запроса (authorization_code)
        code_verifier: Код подтверждения
        device_id: ID устройства
        state: Состояние для CSRF защиты
    """
    device_id: str | None = None
    state: str | None = None
    code_verifier: str | None = None

class OAuthProviderResponse(BaseInputSchema):
    """
    Класс для ответа OAuth авторизации. Используется для получения токена

    Attributes:
        access_token: Токен доступа
        token_type: Тип токена (bearer)
        expires_in: Время жизни токена в секундах
    """

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class YandexTokenData(OAuthProviderResponse):
    """
    Класс для данных токена OAuth авторизации через Яндекс

    Attributes:
        refresh_token: Токен обновления токена
        scope: Область доступа
    """

    refresh_token: str
    scope: str


class GoogleTokenData(OAuthProviderResponse):
    """
    Класс для данных токена OAuth авторизации через Google

    Attributes:
        id_token: Токен идентификации
        scope: Область доступа
    """

    id_token: str
    scope: str


class VKTokenData(OAuthProviderResponse):
    """
    Класс для данных токена OAuth авторизации через VK

    Attributes:
        user_id: Идентификатор пользователя
        email: Электронная почта пользователя
        state: Состояние
        scope: Область доступа
    """

    user_id: int
    email: EmailStr | None = None
    state: str | None = None
    scope: str | None = None


class OAuthUserSchema(RegistrationSchema):
    """
    Схема создания пользователя через OAuth

    см. в RegistrationSchema
    """
    avatar: Optional[str] = None
    vk_id: Optional[int] = None
    google_id: Optional[str] = None
    yandex_id: Optional[int] = None
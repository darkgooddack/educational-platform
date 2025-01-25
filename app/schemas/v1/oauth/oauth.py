import secrets
from enum import Enum
from typing import Optional
from pydantic import EmailStr, BaseModel, Field
from app.schemas.v1.auth.auth import TokenSchema
from app.schemas.v1.auth.register import RegistrationSchema
from ..base import CommonBaseSchema, BaseInputSchema

class OAuthProvider(str, Enum):
    YANDEX = "yandex"
    GOOGLE = "google"
    VK = "vk"

class OAuthConfig(CommonBaseSchema):
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    user_info_url: str
    scope: str
    callback_url: str

class OAuthParams(BaseModel):
    client_id: str
    redirect_uri: str
    scope: str = ""
    response_type: str = "code"

class VKOAuthParams(OAuthParams):
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
        redirect_uri: Путь для перенаправления после авторизации
    """
    refresh_token: str | None = None
    redirect_uri: str = "/"

class OAuthUserData(CommonBaseSchema):
    id: str
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: Optional[str] = None

class YandexUserData(OAuthUserData):
    default_email: EmailStr
    login: str | None = None
    emails: list[EmailStr] | None = None
    psuid: str | None = None

class GoogleUserData(OAuthUserData):
    verified_email: bool = False
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None

class VKUserData(OAuthUserData):
    phone: str | None = None
    user_id: str | None = None

class OAuthTokenParams(BaseModel):
    client_id: str
    client_secret: str
    code: str
    redirect_uri: str
    grant_type: str = "authorization_code"

class OAuthProviderResponse(BaseInputSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class YandexTokenData(OAuthProviderResponse):
    refresh_token: str
    scope: str

class GoogleTokenData(OAuthProviderResponse):
    id_token: str
    scope: str

class VKTokenData(OAuthProviderResponse):
    user_id: int
    email: EmailStr | None = None
    state: str | None = None
    scope: str | None = None

class OAuthUserSchema(RegistrationSchema):
    """
    Схема создания пользователя через OAuth
    """

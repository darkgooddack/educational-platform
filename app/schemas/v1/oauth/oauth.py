from typing import Optional
from pydantic import EmailStr
from app.schemas.v1.auth.register import RegistrationSchema
from ..base import CommonBaseSchema, BaseInputSchema


class OAuthUserSchema(RegistrationSchema):
    """
    Схема создания пользователя через OAuth
    """


class OAuthResponse(BaseInputSchema):
    """
    Схема ответа OAuth авторизации.

    Attributes:
        access_token: Токен доступа
        token_type: Тип токена (bearer)
    """

    access_token: str
    token_type: str = "bearer"


class BaseOAuthUserData(CommonBaseSchema):
    id: str
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: Optional[str] = None

class YandexUserData(BaseOAuthUserData):
    default_email: EmailStr
    login: str | None = None
    emails: list[EmailStr] | None = None
    psuid: str | None = None

class GoogleUserData(BaseOAuthUserData):
    verified_email: bool = False
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None

class VKUserData(BaseOAuthUserData):
    phone: str | None = None
    user_id: str | None = None

class BaseOAuthTokenData(BaseInputSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class YandexTokenData(BaseOAuthTokenData):
    refresh_token: str
    scope: str

class GoogleTokenData(BaseOAuthTokenData):
    id_token: str
    scope: str

class VKTokenData(BaseOAuthTokenData):
    user_id: int
    email: EmailStr | None = None
    state: str | None = None
    scope: str | None = None
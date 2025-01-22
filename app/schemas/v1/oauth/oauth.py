from typing import Optional
from pydantic import EmailStr, Field, HttpUrl
from ..base import CommonBaseSchema, BaseInputSchema


class OAuthUserSchema(BaseInputSchema):
    """
    Схема создания пользователя через OAuth

    Attributes:
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        middle_name (str): Отчество пользователя.
        email (str): Email пользователя.
        phone (str): Телефон пользователя.
        password (str): Пароль пользователя.
        vk_id (str): id пользователя от провайдера vk
        google_id (str): id пользователя от провайдера google
        yandex_id (str): id пользователя от провайдера yandex
    """

    first_name: str = Field(default="Анонимус", min_length=2, max_length=50, description="Имя пользователя")
    last_name: str = Field(default="Пользователь", min_length=2, max_length=50, description="Фамилия пользователя")
    middle_name: Optional[str] = Field(None, max_length=50, description="Отчество пользователя")
    email: EmailStr = Field(description="Email пользователя")
    avatar: Optional[str] = Field(None)
    phone: Optional[str] = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )
    password: str = Field(min_length=8, description="Пароль минимум 8 символов")
    vk_id: Optional[int] = None
    google_id: Optional[int] = None
    yandex_id: Optional[int] = None


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
    avatar: HttpUrl | None = None

class YandexUserData(BaseOAuthUserData):
    default_email: EmailStr
    login: str | None = None
    emails: list[EmailStr] | None = None
    psuid: str | None = None

class GoogleUserData(BaseOAuthUserData):
    verified_email: bool = False
    given_name: str | None = None
    family_name: str | None = None
    picture: HttpUrl | None = None

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
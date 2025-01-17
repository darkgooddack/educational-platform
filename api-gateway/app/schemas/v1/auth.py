"""
Схемы для аутентификации и управления пользователями.
"""

from enum import Enum

from pydantic import EmailStr, Field

from .base import BaseInputSchema


class AuthAction(Enum):
    """
    Действия для аутентификации пользователя.

    Attributes:
        AUTHENTICATE (str): Аутентификация пользователя.
        OAUTH_AUTHENTICATE (str): Аутентификация через OAuth.
        LOGOUT (str): Выход пользователя.
        REGISTER (str): Регистрация пользователя.
    """

    AUTHENTICATE = "authenticate"
    OAUTH_AUTHENTICATE = "oauth_authenticate"
    LOGOUT = "logout"
    REGISTER = "register"


class AuthSchema(BaseInputSchema):
    """
    Схема аутентификации пользователя.

    Attributes:
        email: Email для входа
        password: Пароль пользователя
    """

    email: EmailStr
    password: str = Field(
        min_length=8,
        description="Пароль должен быть минимум 8 символов",
    )


class TokenSchema(BaseInputSchema):
    """
    Схема токена.

    Args:
        access_token (str): Токен доступа.
        token_type (str): Тип токена.
    """

    access_token: str
    token_type: str


class OAuthResponse(BaseInputSchema):
    """
    Схема ответа OAuth авторизации.

    Attributes:
        access_token: Токен доступа
        token_type: Тип токена (bearer)
        provider: Провайдер OAuth (vk/google/yandex)
        email: Email пользователя
    """

    access_token: str
    token_type: str = "bearer"
    provider: str
    email: str

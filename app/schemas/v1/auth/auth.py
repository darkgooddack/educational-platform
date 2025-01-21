"""
Схемы для аутентификации и управления пользователями.
"""

from typing import Optional
from pydantic import EmailStr, Field

from ..base import BaseInputSchema


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
        provider: (str) Провайдер.
        email: (str): Email.
    """

    access_token: str
    token_type: str = "bearer"
    provider: Optional[str] = None
    email: Optional[str] = None

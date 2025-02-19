"""
Схемы для аутентификации и управления пользователями.
"""

from pydantic import EmailStr, Field

from ..base import BaseInputSchema, BaseResponseSchema


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
    token_type: str = "bearer"


class TokenResponseSchema(BaseResponseSchema):
    """
    Схема ответа с токеном доступа

    Swagger UI ожидает строго определенный формат ответа для OAuth2 password flow 
    (access_token и token_type обязательны, другие поля игнорируются)

    Docs:
        https://swagger.io/docs/specification/authentication/oauth2/
        (Из РФ зайти можно только через VPN - санкции)

        https://developer.zendesk.com/api-reference/sales-crm/authentication/requests/#token-request

    Attributes:
        access_token: Токен доступа.
        token_type: Тип токена.
        success: Признак успешной авторизации
        message: Сообщение об успешной авторизации
    """

    access_token: str
    token_type: str = "bearer"
    success: bool = True
    message: str = "Авторизация успешна"

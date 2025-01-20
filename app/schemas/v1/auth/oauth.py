from pydantic import EmailStr, Field

from ..base import BaseInputSchema

class OAuthUserSchema(BaseInputSchema):
    """
    Схема создания пользователя через OAuth

    Attributes:
        email (EmailStr): Email пользователя
        first_name (str): Имя пользователя
        last_name (str): Фамилия пользователя
        middle_name (str): Отчество пользователя
        phone (str): Телефон пользователя
        password (str): Пароль пользователя (генерируется автоматически)
        vk_id (int): ID пользователя в VK
        google_id (int): ID пользователя в Google
        yandex_id (int): ID пользователя в Yandex
    """
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    phone: str | None = None
    password: str = Field(min_length=8)
    vk_id: int | None = None
    google_id: int | None = None
    yandex_id: int | None = None

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
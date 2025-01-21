from pydantic import EmailStr, Field

from typing import Optional
from ..base import BaseInputSchema

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
        provider: Провайдер OAuth (vk/google/yandex)
        email: Email пользователя
    """

    access_token: str
    token_type: str = "bearer"
    provider: str
    email: str
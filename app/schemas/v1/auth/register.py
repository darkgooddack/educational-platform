"""
Схемы для регистрации пользователей.
"""
from typing import Optional
from pydantic import EmailStr, Field

from ..base import BaseInputSchema


class RegistrationSchema(BaseInputSchema):
    """
    Схема создания нового пользователя.

    Attributes:
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        middle_name (str): Отчество пользователя.
        email (str): Email пользователя.
        phone (str): Телефон пользователя.
        password (str): Пароль пользователя.
        vk_id (int): id пользователя от провайдера vk
        google_id (str): id пользователя от провайдера google
        yandex_id (int): id пользователя от провайдера yandex
    """

    first_name: str = Field(min_length=0, max_length=50, description="Имя пользователя")
    last_name: str = Field(
        min_length=0, max_length=50, description="Фамилия пользователя"
    )
    middle_name: str | None = Field(
        None, max_length=50, description="Отчество пользователя"
    )
    email: EmailStr = Field(description="Email пользователя")
    phone: str | None = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )
    avatar: Optional[str] = None
    password: str = Field(min_length=8, description="Пароль минимум 8 символов")
    vk_id: Optional[int] = None
    google_id: Optional[str] = None
    yandex_id: Optional[int] = None

class RegistrationResponseSchema(BaseInputSchema):
    """
    Схема ответа при успешной регистрации

    Attributes:
        user_id (int): ID пользователя
        email (str): Email пользователя
        message (str): Сообщение об успешной регистрации
    """

    user_id: int
    email: EmailStr
    message: str = "Регистрация успешно завершена"

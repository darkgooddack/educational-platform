"""
Схемы для регистрации пользователей.
"""

from pydantic import Field, EmailStr
from .base import BaseInputSchema

class CreateUserSchema(BaseInputSchema):
    """
    Схема создания нового пользователя.

    Attributes:
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        middle_name (str): Отчество пользователя.
        email (str): Email пользователя.
        phone (str): Телефон пользователя.
        password (str): Пароль пользователя.
    """

    first_name: str = Field(
        min_length=2,
        max_length=50,
        description="Имя пользователя"
    )
    last_name: str = Field(
        min_length=2,
        max_length=50,
        description="Фамилия пользователя"
    )
    middle_name: str | None = Field(
        None,
        max_length=50,
        description="Отчество пользователя"
    )
    email: EmailStr = Field(description="Email пользователя")
    phone: str = Field(
        pattern=r'^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$',
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"]
    )
    password: str = Field(
        min_length=8,
        description="Пароль минимум 8 символов"
    )
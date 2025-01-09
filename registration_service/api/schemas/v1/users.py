from typing import Optional
from enum import Enum
from pydantic import Field, EmailStr
from app.schemas.v1.base import BaseInputSchema


class UserRole(str, Enum):
    """
    Роли пользователя в системе.

    Args:
        ADMIN (str): Роль администратора.
        MODERATOR (str): Роль модератора.
        USER (str): Роль пользователя.
    """

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class RegistrationUserSchema(BaseInputSchema):
    """
    Схема создания пользователя.
    #! Для примера
    Args:
        name (str): Имя пользователя.
        email (str): Email пользователя.
        password (str): Пароль пользователя.
    """

    name: str = Field(
        min_length=4,
        max_length=20,
        description="Имя пользователя должно быть от 4 до 20 символов",
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        description="Пароль должен быть минимум 8 символа",
    )


class RegistrationSchema(BaseInputSchema):
    """
    Схема пользователя.
    #! Для примера
    Args:
        name (str): Имя пользователя.
        email (str): Email пользователя.
        hashed_password (str | None): Хешированный пароль пользователя.
    """

    id: Optional[int] = None
    name: str
    email: str
    hashed_password: str | None = None

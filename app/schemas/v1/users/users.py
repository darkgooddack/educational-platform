"""
Модуль схем пользователя.
"""

from enum import Enum
from pydantic import Field
from app.schemas.v1.auth.register import RegistrationSchema
from ..base import BaseInputSchema


class UserRole(str, Enum):
    """
    Роли пользователя в системе.

    Attributes:
        ADMIN (str): Роль администратора.
        MODERATOR (str): Роль модератора.
        USER (str): Роль пользователя.
        MANAGER (str): Роль менеджера.
        TUTOR (str): Роль наставника.
    """

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    MANAGER = "manager"
    TUTOR = "tutor"


class UserSchema(BaseInputSchema):
    """
    Схема пользователя.

    Attributes:
        id (int): Идентификатор пользователя.
        name (str): Имя пользователя (необязательно).
        email (str): Email пользователя.
        hashed_password (str | None): Хешированный пароль пользователя.
    """

    id: int | None = None
    name: str | None = None
    email: str
    hashed_password: str | None = None

class UserCreateSchema(RegistrationSchema):
    """
    Схема создания пользователя.

    см. в RegistrationSchema
    """


class UserUpdateSchema(BaseInputSchema):
    """
        Схема обновления данных пользователя

        Attributes:
            first_name (str | None): Имя пользователя.
            last_name (str | None): Фамилия пользователя.
            middle_name (str | None): Отчество пользователя.
            phone (str | None): Телефон пользователя.
    """
    first_name: str | None = Field(None, min_length=2, max_length=50)
    last_name: str | None = Field(None, min_length=2, max_length=50)
    middle_name: str | None = Field(None, max_length=50)
    phone: str | None = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )

    class Config:
        extra = "forbid"

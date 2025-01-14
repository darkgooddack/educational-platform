"""
Модуль схем пользователя.
"""

from enum import Enum

from .base import BaseInputSchema


class UserRole(str, Enum):
    """
    Роли пользователя в системе.

    Attributes:
        ADMIN (str): Роль администратора.
        MODERATOR (str): Роль модератора.
        USER (str): Роль пользователя.
    """

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class UserSchema(BaseInputSchema):
    """
    Схема пользователя.

    Attributes:
        name (str): Имя пользователя (необязательно).
        email (str): Email пользователя.
        hashed_password (str | None): Хешированный пароль пользователя.
    """
    name: str | None = None
    email: str
    hashed_password: str | None = None

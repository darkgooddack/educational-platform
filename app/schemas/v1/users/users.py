"""
Модуль схем пользователя.
"""

from enum import Enum
from typing import Optional

from pydantic import EmailStr, Field

from app.schemas.v1.auth.register import RegistrationSchema

from ..base import BaseInputSchema, CommonBaseSchema


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


class UserSchema(CommonBaseSchema):
    """
    Схема пользователя.

    Attributes:
        id (int): ID пользователя.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        middle_name (str): Отчество пользователя.
        email (EmailStr): Email пользователя.
        phone (str): Телефон пользователя.
        avatar (str): Ссылка на аватар пользователя.
        is_active (bool): Флаг активности пользователя.
        role (UserRole): Роль пользователя.
    """

    id: int
    first_name: str
    last_name: str
    middle_name: str | None
    email: EmailStr
    phone: str | None
    avatar: Optional[str] = None
    is_active: bool
    role: UserRole


class UserCredentialsSchema(BaseInputSchema):
    """
    Схема учетных данных пользователя.


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


class ManagerSelectSchema(BaseInputSchema):
    """
    Схема для выбора менеджеров в форме обратной связи.

    Attributes:
        id (int): Идентификатор менеджера.
        first_name (str): Имя менеджера.
        last_name (str): Фамилия менеджера.
        middle_name (Optional[str]): Отчество менеджера (необязательно).
        email (Optional[str]): Email менеджера (необязательно).
        avatar (Optional[str]): URL-адрес аватара менеджера (необязательно).
    """

    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool


class UserResponseSchema(BaseInputSchema):
    """
    Схема ответа пользователя.

    Attributes:
        id (int): Идентификатор пользователя.
        name (str): Имя пользователя.
        email (str): Email пользователя.
        role (UserRole): Роль пользователя.
    """

    id: int
    name: str
    email: str
    role: UserRole
    message: str = Field(
        default="Пользователь успешно создан!",
        description="Сообщение, отправляемое после совершенной работы с пользователем",
        examples=["Пользователь успешно создан!", "Роль успешно назначена!"],
    )

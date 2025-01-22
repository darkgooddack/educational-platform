"""
Модуль, содержащий модели данных для работы с пользователями.

Этот модуль определяет следующие модели SQLAlchemy:
- UserModel: представляет пользователя в системе.

Модель наследуется от базового класса BaseModel и определяет
соответствующие поля и отношения между таблицами базы данных.

Модель использует типизированные аннотации Mapped для определения полей,
что обеспечивает улучшенную поддержку статической типизации.

Этот модуль предназначен для использования в сочетании с SQLAlchemy ORM
для выполнения операций с базой данных, связанных с пользователями.
"""
from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseModel
from app.schemas import UserRole


class UserModel(BaseModel):
    """
    Модель для представления пользователей.

    Attributes:
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        middle_name (str): Отчество пользователя.
        email (str): Электронная почта пользователя.
        phone (str): Номер телефона пользователя.
        hashed_password (str): Хэшированный пароль пользователя.
        role (UserRole): Роль пользователя в системе.
        avatar_url (str): Ссылка на аватар пользователя.
        vk_id (int): ID пользователя в VK.
        google_id (int): ID пользователя в Google (BigInteger).
        yandex_id (int): ID пользователя в Yandex.

    """

    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    middle_name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    avatar: Mapped[str] = mapped_column(nullable=True)
    vk_id: Mapped[int] = mapped_column(unique=True, nullable=True)
    google_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    yandex_id: Mapped[int] = mapped_column(unique=True, nullable=True)

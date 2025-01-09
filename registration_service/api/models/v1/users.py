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
from sqlalchemy.orm import Mapped, mapped_column
from api.models.v1.base import BaseModel
from api.schemas.v1.users import UserRole


class UserModel(BaseModel):
    """
    Модель для представления пользователей.
    #! Для примера
    Args:
        name (str): Имя пользователя.
        email (str): Электронная почта пользователя.
        role (UserRole): Роль пользователя в системе.
        hashed_password (str): Хэшированный пароль пользователя.
        avatar_url (str): Ссылка на аватар пользователя.

    """

    __tablename__ = "users"

    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str]
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    avatar_url: Mapped[str] = mapped_column(nullable=True)

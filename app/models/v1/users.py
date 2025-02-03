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
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel
from app.models.v1.feedbacks import FeedbackModel
from app.models.v1.videos import VideoLectureModel
from app.models.v1.tests import TestModel
from app.models.v1.lectures import LectureModel
from app.models.v1.posts import PostModel
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
        avatar (str): Ссылка на аватар пользователя.
        is_active (bool): Флаг активности пользователя.
        is_online (bool): Флаг онлайн-статуса пользователя.
        last_seen (datetime): Дата и время последнего визита пользователя.
        vk_id (int): ID пользователя в VK.
        google_id (str): ID пользователя в Google.
        yandex_id (int): ID пользователя в Yandex.

    Relationships:
        feedbacks (list[FeedbackModel]): Список обратных связей пользователя (для менеджеров UserRole.MANAGER)
        video_lectures (list[VideoLectureModel]): Список видео лекций, созданных пользователем.
        tests (list[TestModel]): Список тестов, созданных пользователем.
        lectures (list[LectureModel]): Список лекций, созданных пользователем.
        posts (list[PostModel]): Список постов, созданных пользователем.
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
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_online: Mapped[bool] = mapped_column(default=False, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    vk_id: Mapped[int] = mapped_column(unique=True, nullable=True)
    google_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    yandex_id: Mapped[int] = mapped_column(unique=True, nullable=True)

    feedbacks: Mapped[list["FeedbackModel"]] = relationship(
        "FeedbackModel", back_populates="manager", lazy="joined"
    )
    video_lectures: Mapped[list["VideoLectureModel"]] = relationship(
        "VideoLectureModel", back_populates="author", lazy="dynamic"
    )
    tests: Mapped[list["TestModel"]] = relationship("TestModel", back_populates="author", lazy="dynamic")
    lectures: Mapped[list["LectureModel"]] = relationship("LectureModel", back_populates="author")
    posts: Mapped[list["PostModel"]] = relationship("PostModel", back_populates="author")
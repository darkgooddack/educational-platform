from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel
from app.models.v1 import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.v1.users import UserModel

class VideoLectureModel(BaseModel):
    """
    Модель для представления видео лекций.

    Attributes:
        title (str): Название видео лекции.
        description (str): Описание видео лекции.
        theme (str): Тематика видео лекции.
        views (int): Количество просмотров.
        video_url (str): Ссылка на видео.
        duration (int): Длительность видео в секундах.
        author_id (int): ID автора видео лекции (внешний ключ).
        thumbnail_url (str): URL-адрес миниатюры видео.

    Relationships:
        author (UserModel): Связь с автором видео лекции.
    """

    __tablename__ = "video_lectures"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    theme: Mapped[str] = mapped_column(nullable=False)
    views: Mapped[int] = mapped_column(default=0, nullable=False)  # По умолчанию 0 просмотров
    video_url: Mapped[str] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)  # Длительность в секундах
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(nullable=True)
    # Связь с автором (пользователем)
    author: Mapped["UserModel"] = relationship("UserModel", back_populates="video_lectures", lazy="joined")
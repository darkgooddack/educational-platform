from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel
from app.models.v1 import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.v1.users import UserModel
    from app.models.v1.videos import VideoLectureModel

class ThemeModel(BaseModel):
    """
    Модель для представления тем курсов.

    Attributes:
        name (str): Название темы курса.
        description (str): Описание темы курса.
        parent_id (int): ID родительской темы (внешний ключ).

    Relationships:
        video_lectures (list[VideoLectureModel]): Связь с видео лекциями, относящимися к теме.
        tests (list[TestModel]): Связь с тестами, относящимися к теме.
    """

    __tablename__ = "themes"

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey("themes.id"), nullable=True)
    
    video_lectures: Mapped[list["VideoLectureModel"]] = relationship("VideoLectureModel", back_populates="theme", lazy="dynamic")
    tests: Mapped[list["TestModel"]] = relationship("TestModel", back_populates="theme", lazy="dynamic")

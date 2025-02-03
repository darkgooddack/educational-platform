
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.v1.base import BaseModel
from app.models.v1 import TYPE_CHECKING
from app.schemas import ContentType
if TYPE_CHECKING:
    from app.models.v1.users import UserModel
    from app.models.v1.themes import ThemeModel
    from app.models.v1.tests import TestModel



class LectureModel(BaseModel):
    """
    Модель для представления лекций.
    
    Attributes:
        title (str): Заголовок лекции.
        description (str): Описание лекции.
        theme_id (int): ID темы, к которой относится лекция.
        author_id (int): ID автора лекции.
        views (int): Количество просмотров лекции.

    Relationships:
        theme (ThemeModel): Связь с темой, к которой относится лекция.
        author (UserModel): Связь с автором лекции.
        content_blocks (list[ContentBlockModel]): Связь с блоками контента лекции.
        tests (list[TestModel]): Связь с тестами, относящимися к лекции.
    """
    __tablename__ = "lectures"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    views: Mapped[int] = mapped_column(default=0, nullable=False)
    
    content_blocks: Mapped[list["ContentBlockModel"]] = relationship(
        "ContentBlockModel", 
        back_populates="lecture", 
        order_by="ContentBlockModel.order",
        cascade="all, delete-orphan"
    )
    author: Mapped["UserModel"] = relationship("UserModel", back_populates="lectures")
    theme: Mapped["ThemeModel"] = relationship("ThemeModel", back_populates="lectures")
    tests: Mapped[list["TestModel"]] = relationship("TestModel", back_populates="lecture")



class LectureContentBlockModel(BaseModel):
    """
    Модель блока контента в лекции

    Attributes:
        lecture_id (int): ID лекции, к которой относится блок контента.
        type (ContentType): Тип блока контента.
        content (str): Содержимое блока контента.
        order (int): Порядок блока контента.
        caption (str): Подпись к блоку контента.
    
    Relationships:
        lecture (LectureModel): Связь с лекцией, к которой относится блок контента.
    """
    __tablename__ = "lecture_content_blocks"

    lecture_id: Mapped[int] = mapped_column(ForeignKey("lectures.id"), nullable=False)
    type: Mapped[ContentType] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)  # URL для медиа или текст/код
    order: Mapped[int] = mapped_column(nullable=False)  # Порядок блоков
    caption: Mapped[str] = mapped_column(nullable=True)  # Подпись к блоку
    
    lecture: Mapped["LectureModel"] = relationship("LectureModel", back_populates="content_blocks")
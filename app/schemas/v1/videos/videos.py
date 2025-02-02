from fastapi import UploadFile
from ..base import CommonBaseSchema, BaseSchema, BaseInputSchema
from pydantic import Field

class VideoLectureSchema(CommonBaseSchema):
    """
    Схема для представления видео лекции.

    Attributes:
        title (str): Название видео лекции.
        description (str): Описание видео лекции.
        theme (str): Тематика видео лекции.
        views (int): Количество просмотров.
        video_url (str): Ссылка на видео.
        duration (int): Длительность видео в секундах.
        author_id (int): ID автора видео лекции.
    """
    title: str = Field(
        min_length=0,
        max_length=50,
        description="Наименование видео лекции"
    )
    description: str = Field(
        min_length=0,
        max_length=200,
        description="Описание видео лекции"
    )
    theme: str = Field(
        min_length=0,
        max_length=50,
        description="Тематика видео лекции"
    )
    views: int = Field(
        default=0,
        description="Количество просмотров"
    )
    video_url: str = Field(
        description="Ссылка на видео"
    )
    duration: int = Field(
        description="Длительность видео в секундах"
    )
    author_id: int = Field(
        description="ID автора видео лекции"
    )
    thumbnail_url: str = Field(
        description="Ссылка на миниатюру видео"
    )
class VideoLectureCreateSchema(BaseInputSchema):
    """
    Схема для создания видео лекции.

    Attributes:
        title (str): Название видео лекции.
        description (str): Описание видео лекции.
        video_file (UploadFile): Файл видео лекции.

    """
    title: str = Field(
        min_length=0,
        max_length=50,
        description="Наименование видео лекции"
    )
    description: str = Field(
        min_length=0,
        max_length=200,
        description="Описание видео лекции"
    )
    video_file: UploadFile
    thumbnail_file: UploadFile

class VideoLectureResponseSchema(BaseInputSchema):
    """
    Схема ответа при успешной дообавлении видео лекции.

    Attributes:
        user_id (int): ID пользователя
        video_url (str): Ссылка на видео.
        message (str): Сообщение об успешной регистрации
    """

    user_id: int
    video_url: str
    thumbnail_url: str
    message: str = "Видео успешно добавлено"
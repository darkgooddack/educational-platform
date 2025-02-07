from typing import List, Optional
from fastapi import UploadFile
from pydantic import Field
from ..base import BaseSchema, BaseInputSchema, ListResponseSchema


class VideoLectureBase(BaseSchema):
    """
    Схема для представления видео лекции.

    Attributes:
        title (str): Название видео лекции.
        description (str): Описание видео лекции.
        theme_id (int): Тематика видео лекции.
        views (int): Количество просмотров.
        video_url (str): Ссылка на видео.
        duration (int): Длительность видео в секундах.
        author_id (int): ID автора видео лекции.
        thumbnail_url (str): URL-адрес миниатюры видео.
    """
    title: str = Field(min_length=0, max_length=50)
    description: str = Field(min_length=0, max_length=200)
    theme_id: Optional[int] = None
    views: int = Field(default=0)
    video_url: str
    duration: int
    author_id: int
    thumbnail_url: str

class VideoLectureCreateSchema(BaseInputSchema):
    """
    Схема для создания видео лекции.

    Attributes:
        title (str): Название видео лекции.
        description (str): Описание видео лекции.
        theme_id (int): Тематика видео лекции.
        video_file (UploadFile): Файл видео лекции.
        thumbnail_file (UploadFile): Файл миниатюры видео лекции.

    """
    title: str = Field(min_length=0, max_length=50)
    description: str = Field(min_length=0, max_length=200)
    theme_id: int
    video_file: UploadFile
    thumbnail_file: UploadFile

class VideoLectureSchema(VideoLectureBase):
    """Полная схема видео-лекции"""
    pass

class VideoLectureResponseSchema(BaseInputSchema):
    """
    Схема ответа при успешной дообавлении видео лекции.

    Attributes:
        user_id (int): ID пользователя
        video_url (str): Ссылка на видео.
        thumbnail_url (str): Ссылка на миниатюру видео.
        message (str): Сообщение об успешной регистрации
    """

    user_id: int
    video_url: str
    thumbnail_url: str
    message: str = "Видео успешно добавлено"

class VideoLectureListResponse(ListResponseSchema[VideoLectureSchema]):
    """Схема для списка видео-лекций"""
    items: List[VideoLectureSchema]
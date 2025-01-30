from ..base import BaseSchema, BaseInputSchema, CommonBaseSchema

class VideoLectureSchema(BaseSchema):
    """
    Схема для представления видео лекции.

    Attributes:
        title (str): Название видео лекции.
        description (str): Описание видео лекции.
        theme (str): Тематика видео лекции.
        views (int): Количество просмотров.
        video_url (HttpUrl): Ссылка на видео.
        duration (int): Длительность видео в секундах.
        author_id (int): ID автора видео лекции.
    """
    title: str
    description: str
    theme: str
    views: int = 0  # По умолчанию 0 просмотров
    video_url: HttpUrl
    duration: int
    author_id: int

from enum import Enum


class ContentType(str, Enum):
    """
    Перечисление типов контента

    Attributes:
        TEXT (str): Текстовый контент
        IMAGE (str): Изображение
        VIDEO (str): Видео
        AUDIO (str): Аудио
        CODE (str): Код
    """

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CODE = "code"

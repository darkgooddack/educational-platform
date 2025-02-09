"""
Пакет моделей данных.

Предоставляет единую точку доступа ко всем моделям приложения.
"""

from .v1.base import BaseModel
from .v1.feedbacks import FeedbackModel
from .v1.lectures import LectureContentBlockModel, LectureModel
from .v1.posts import PostContentBlockModel, PostModel, PostTagModel, TagModel
from .v1.tests import AnswerModel, QuestionModel, TestModel
from .v1.themes import ThemeModel
from .v1.users import UserModel
from .v1.videos import VideoLectureModel

__all__ = [
    "BaseModel",
    "UserModel",
    "FeedbackModel",
    "VideoLectureModel",
    "LectureModel",
    "LectureContentBlockModel",
    "TestModel",
    "QuestionModel",
    "AnswerModel",
    "PostModel",
    "TagModel",
    "PostTagModel",
    "PostContentBlockModel",
    "ThemeModel",
]

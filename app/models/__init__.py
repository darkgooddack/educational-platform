"""
Пакет моделей данных.

Предоставляет единую точку доступа ко всем моделям приложения.
"""

from .v1.base import BaseModel
from .v1.feedbacks import FeedbackModel
from .v1.users import UserModel
from .v1.videos import VideoLectureModel
from .v1.lectures import LectureModel
from .v1.tests import TestModel
from .v1.posts import PostModel, TagModel, PostTagModel
from .v1.themes import ThemeModel

__all__ = [
    "BaseModel", 
    "UserModel", 
    "FeedbackModel", 
    "VideoLectureModel",
    "LectureModel",
    "TestModel",
    "PostModel",
    "TagModel",
    "PostTagModel",
    "ThemeModel"
    ]

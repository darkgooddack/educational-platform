"""
Пакет моделей данных.

Предоставляет единую точку доступа ко всем моделям приложения.
"""

from .v1.base import BaseModel
from .v1.users import UserModel
from .v1.feedbacks import FeedbackModel

__all__ = ["BaseModel", "UserModel", "FeedbackModel"]

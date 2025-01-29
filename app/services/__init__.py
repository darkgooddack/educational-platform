"""
Пакет сервисов приложения.

Предоставляет единую точку доступа ко всем сервисам.
"""

from .v1.auth.service import AuthService
from .v1.base import BaseDataManager, BaseEntityManager, BaseService
from .v1.feedbacks import FeedbackDataManager, FeedbackService
from .v1.oauth import OAuthService
from .v1.users import UserDataManager, UserService

__all__ = [
    "BaseService",
    "BaseDataManager",
    "BaseEntityManager",
    "UserService",
    "UserDataManager",
    "AuthService",
    "OAuthService",
    "FeedbackService",
    "FeedbackDataManager",
]

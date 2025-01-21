"""
Пакет сервисов приложения.

Предоставляет единую точку доступа ко всем сервисам.
"""
from .v1.base import BaseService, BaseDataManager, BaseEntityManager
from .v1.users import UserService, UserDataManager
from .v1.auth.service import AuthService
from .v1.oauth import OAuthService

__all__ = [
    "BaseService",
    "BaseDataManager",
    "BaseEntityManager",
    "UserService",
    "UserDataManager",
    "AuthService",
    "OAuthService"
]
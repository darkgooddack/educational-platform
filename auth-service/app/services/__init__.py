"""
Пакет сервисов приложения.

Предоставляет единую точку доступа ко всем сервисам.
"""

from .v1.auth import AuthDataManager, AuthService
from .v1.users import UserDataManager, UserService

__all__ = [
    "UserService",
    "UserDataManager",
    "AuthService",
    "AuthDataManager",
]

"""
Пакет сервисов приложения.

Предоставляет единую точку доступа ко всем сервисам.
"""

from .v1.authentication import AuthenticationDataManager, AuthenticationService
from .v1.users import UserDataManager, UserService

__all__ = [
    "UserService",
    "UserDataManager",
    "AuthenticationService",
    "AuthenticationDataManager",
]

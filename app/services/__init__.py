"""
Пакет сервисов приложения.

Предоставляет единую точку доступа ко всем сервисам.
"""

from .v1.auth.auth import AuthDataManager, AuthService
from .v1.auth.oauth import OAuthService
from .v1.auth.users import UserDataManager, UserService

__all__ = [
    "UserService",
    "UserDataManager",
    "AuthService",
    "AuthDataManager",
    "OAuthService",
]

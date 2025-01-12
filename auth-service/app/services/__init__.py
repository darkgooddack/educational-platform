"""
Пакет сервисов приложения.

Предоставляет единую точку доступа ко всем сервисам.
"""

from .v1.base import BaseService, BaseDataManager, BaseEntityManager
from .v1.users import UserService, UserDataManager
from .v1.authentication import AuthenticationService, AuthenticationDataManager

__all__ = [
    "BaseService",
    "BaseDataManager",
    "BaseEntityManager",
    "UserService",
    "UserDataManager",
    "AuthenticationService",
    "AuthenticationDataManager"
]

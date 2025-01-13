"""
Пакет сервисов приложения.

Предоставляет единую точку доступа ко всем сервисам.
"""

from .v1.base import BaseDataManager, BaseEntityManager, BaseService
from .v1.users import UserDataManager, UserService
from .v1.authentication import AuthenticationDataManager, AuthenticationService


__all__ = [
    "BaseService",
    "BaseDataManager",
    "BaseEntityManager",
    "UserService",
    "UserDataManager",
    "AuthenticationService",
    "AuthenticationDataManager",
]

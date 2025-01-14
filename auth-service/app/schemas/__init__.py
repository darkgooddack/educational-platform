"""
Пакет схем данных.

Предоставляет единую точку доступа ко всем Pydantic схемам.
"""

from .v1.authentication import AuthenticationSchema, TokenSchema
from .v1.base import BaseInputSchema, BaseSchema
from .v1.registration import CreateUserSchema, OAuthUserSchema
from .v1.users import UserRole, UserSchema

__all__ = [
    "BaseSchema",
    "BaseInputSchema",
    "OAuthUserSchema",
    "CreateUserSchema",
    "UserSchema",
    "TokenSchema",
    "UserRole",
    "AuthenticationSchema",
]

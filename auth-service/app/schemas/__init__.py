"""
Пакет схем данных.

Предоставляет единую точку доступа ко всем Pydantic схемам.
"""
from .v1.base import BaseSchema, BaseInputSchema
from .v1.users import UserRole, UserSchema
from .v1.authentication import AuthenticationSchema, TokenSchema
from .v1.registration import CreateUserSchema


__all__ = [
    "BaseSchema",
    "BaseInputSchema",
    "CreateUserSchema",
    "UserSchema",
    "TokenSchema",
    "UserRole",
    "AuthenticationSchema"
]
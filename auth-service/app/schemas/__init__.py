"""
Пакет схем данных.

Предоставляет единую точку доступа ко всем Pydantic схемам.
"""

from .v1.auth import AuthSchema, TokenSchema
from .v1.base import BaseInputSchema, BaseSchema
from .v1.register import (OAuthUserSchema, RegistrationResponseSchema,
                              RegistrationSchema)
from .v1.users import UserRole, UserSchema

__all__ = [
    "BaseSchema",
    "BaseInputSchema",
    "OAuthUserSchema",
    "RegistrationSchema",
    "RegistrationResponseSchema",
    "UserSchema",
    "TokenSchema",
    "UserRole",
    "AuthSchema",
]

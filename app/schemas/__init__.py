"""
Пакет схем данных.

Предоставляет единую точку доступа ко всем Pydantic схемам.
"""

from .v1.base import BaseInputSchema, BaseSchema
from .v1.auth.auth import AuthSchema, TokenSchema
from .v1.auth.oauth import OAuthUserSchema, OAuthResponse
from .v1.auth.register import RegistrationResponseSchema, RegistrationSchema
from .v1.auth.users import UserRole, UserSchema, UserUpdateSchema

__all__ = [
    "BaseSchema",
    "BaseInputSchema",
    "OAuthUserSchema",
    "OAuthResponse",
    "RegistrationSchema",
    "RegistrationResponseSchema",
    "UserSchema",
    "UserUpdateSchema",
    "TokenSchema",
    "UserRole",
    "AuthSchema",
]

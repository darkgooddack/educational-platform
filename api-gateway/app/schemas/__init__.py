"""
Пакет схем данных.

Предоставляет единую точку доступа ко всем Pydantic схемам.
"""

from .v1.auth import AuthSchema, OAuthResponse, TokenSchema
from .v1.base import BaseInputSchema, BaseSchema, CommonBaseSchema
from .v1.cache import RouteCacheSchema, TokenCacheSchema
from .v1.register import RegistrationResponseSchema, RegistrationSchema

__all__ = [
    "BaseSchema",
    "BaseInputSchema",
    "CommonBaseSchema",
    "AuthSchema",
    "TokenSchema",
    "OAuthResponse",
    "TokenCacheSchema",
    "RouteCacheSchema",
    "RegistrationSchema",
    "RegistrationResponseSchema",
]

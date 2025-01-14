"""
Пакет схем данных.

Предоставляет единую точку доступа ко всем Pydantic схемам.
"""

from .v1.base import BaseInputSchema, BaseSchema, CommonBaseSchema
from .v1.cache import RouteCacheSchema, TokenCacheSchema
from .v1.authentication import AuthenticationSchema, TokenSchema, OAuthResponse
from .v1.registration import RegistrationSchema, RegistrationResponseSchema

__all__ = [
    "BaseSchema",
    "BaseInputSchema",
    "CommonBaseSchema",
    "AuthenticationSchema",
    "TokenSchema",
    "OAuthResponse",
    "TokenCacheSchema",
    "RouteCacheSchema",
    "RegistrationSchema",
    "RegistrationResponseSchema",

]
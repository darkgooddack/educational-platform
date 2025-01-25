"""
Пакет схем данных.

Предоставляет единую точку доступа ко всем Pydantic схемам.
"""

from .v1.base import BaseInputSchema, BaseSchema
from .v1.auth.auth import AuthSchema, TokenSchema
from .v1.oauth.oauth import (
    OAuthUserSchema,
    OAuthResponse,
    OAuthUserData,
    YandexUserData,
    GoogleUserData,
    VKUserData,
    OAuthProvider,
    OAuthProviderResponse,
    OAuthTokenParams,
    OAuthConfig,
    OAuthParams,
    VKOAuthParams

)
from .v1.auth.register import RegistrationResponseSchema, RegistrationSchema
from .v1.users.users import UserRole, UserSchema, UserUpdateSchema

__all__ = [
    "BaseSchema",
    "BaseInputSchema",
    "OAuthUserSchema",
    "OAuthResponse",
    "OAuthConfig",
    "OAuthParams",
    "OAuthProvider",
    "OAuthProviderResponse",
    "OAuthTokenParams",
    "VKOAuthParams",
    "RegistrationSchema",
    "RegistrationResponseSchema",
    "UserSchema",
    "UserUpdateSchema",
    "TokenSchema",
    "UserRole",
    "AuthSchema",
    "OAuthUserData",
    "YandexUserData",
    "GoogleUserData",
    "VKUserData"
]

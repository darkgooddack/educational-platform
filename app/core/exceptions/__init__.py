"""
Пакет исключений приложения.

Предоставляет централизованный доступ ко всем кастомным исключениям.

Example:
    >>> from app.core.exceptions import UserNotFoundError, UserExistsError
    >>> raise UserNotFoundError(user_id=42)
"""
from .v1.base import BaseAPIException
from .v1.auth.auth import (
    AuthenticationError,
    InvalidCredentialsError,
    InvalidEmailFormatError,
    InvalidPasswordError,
    WeakPasswordError,
    )

from .v1.auth.oauth import (
    OAuthError,
    InvalidProviderError,
    OAuthConfigError,
    OAuthTokenError,
    OAuthUserDataError,
    OAuthInvalidGrantError
)

from .v1.auth.users import (
    UserExistsError,
    UserNotFoundError,
    UserCreationError
)
from .v1.auth.security import (
    TokenInvalidError,
    TokenExpiredError,
    TokenMissingError
)

__all__ = [
    "BaseAPIException",
    "AuthenticationError",
    "InvalidCredentialsError",
    "InvalidEmailFormatError",
    "InvalidPasswordError",
    "WeakPasswordError",
    "TokenInvalidError",
    "TokenMissingError",
    "TokenExpiredError",
    "OAuthError",
    "InvalidProviderError",
    "OAuthConfigError",
    "OAuthTokenError",
    "OAuthUserDataError",
    "OAuthInvalidGrantError",
    "UserExistsError",
    "UserNotFoundError",
    "UserCreationError"
]

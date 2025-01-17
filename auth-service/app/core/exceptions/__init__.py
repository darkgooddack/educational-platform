"""
Пакет исключений приложения.

Предоставляет централизованный доступ ко всем кастомным исключениям.

Example:
    >>> from app.core.exceptions import UserNotFoundError, UserExistsError
    >>> raise UserNotFoundError(user_id=42)
"""

from .v1.auth import (AuthError, InvalidCredentialsError,
                                InvalidPasswordError, TokenExpiredError,
                                TokenMissingError)
from .v1.base import BaseAPIException
from .v1.users import (InvalidEmailFormatError, UserExistsError,
                       UserNotFoundError, WeakPasswordError)

__all__ = [
    "BaseAPIException",
    "TokenMissingError",
    "TokenExpiredError",
    "InvalidCredentialsError",
    "InvalidPasswordError",
    "AuthError",
    "UserNotFoundError",
    "UserExistsError",
    "InvalidEmailFormatError",
    "WeakPasswordError",
]

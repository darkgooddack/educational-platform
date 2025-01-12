"""
Пакет исключений приложения.

Предоставляет централизованный доступ ко всем кастомным исключениям.

Example:
    >>> from app.core.exceptions import UserNotFoundError, UserExistsError
    >>> raise UserNotFoundError(user_id=42)
"""
from .v1.base import BaseAPIException
from .v1.users import UserNotFoundError, UserExistsError, InvalidEmailFormatError, WeakPasswordError
from .v1.authentication import (
    TokenMissingError,
    TokenExpiredError,
    InvalidCredentialsError,
    AuthenticationError,
    InvalidPasswordError
)


__all__ = [
    "BaseAPIException",
    "TokenMissingError",
    "TokenExpiredError",
    "InvalidCredentialsError",
    "InvalidPasswordError",
    "AuthenticationError",
    "UserNotFoundError",
    "UserExistsError",
    "InvalidEmailFormatError",
    "WeakPasswordError"
]

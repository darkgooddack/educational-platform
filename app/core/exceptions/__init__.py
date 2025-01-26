"""
Пакет исключений приложения.

Предоставляет централизованный доступ ко всем кастомным исключениям.

Example:
    >>> from app.core.exceptions import UserNotFoundError, UserExistsError
    >>> raise UserNotFoundError(user_id=42)
"""

from .v1.auth.auth import (AuthenticationError, InvalidCredentialsError,
                           InvalidEmailFormatError, InvalidPasswordError,
                           WeakPasswordError)
from .v1.auth.oauth import (InvalidCallbackError, InvalidProviderError,
                            InvalidReturnURLError, OAuthConfigError,
                            OAuthError, OAuthInvalidGrantError,
                            OAuthTokenError, OAuthUserCreationError,
                            OAuthUserDataError)
from .v1.auth.security import (TokenExpiredError, TokenInvalidError,
                               TokenMissingError)
from .v1.auth.users import (UserCreationError, UserExistsError,
                            UserNotFoundError)
from .v1.base import BaseAPIException, DatabaseError, ValueNotFoundError
from .v1.feedback.feedback import FeedbackAddError

__all__ = [
    "BaseAPIException",
    "DatabaseError",
    "ValueNotFoundError",
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
    "OAuthUserCreationError",
    "InvalidReturnURLError",
    "InvalidCallbackError",
    "UserExistsError",
    "UserNotFoundError",
    "UserCreationError",
    "FeedbackAddError",
]

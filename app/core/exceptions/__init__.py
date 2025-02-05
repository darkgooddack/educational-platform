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
from .v1.users.users import (UserCreationError, UserExistsError,
                            UserNotFoundError, UserInactiveError)
from .v1.base import BaseAPIException, DatabaseError, ValueNotFoundError
from .v1.feedback.feedback import FeedbackAddError, FeedbackDeleteError, FeedbackGetError, FeedbackUpdateError
from .v1.themes.themes import ThemeNotFoundError, ThemeExistsError
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
    "UserInactiveError",
    "UserNotFoundError",
    "UserCreationError",
    "FeedbackAddError",
    "FeedbackDeleteError",
    "FeedbackGetError",
    "FeedbackUpdateError",
    "ThemeNotFoundError", 
    "ThemeExistsError"
]

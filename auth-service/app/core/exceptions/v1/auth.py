"""
Исключения для аутентификации и управления пользователями.

Provides:
    - TokenMissingError: Отсутствие токена
    - InvalidCredentialsError: Неверные учетные данные
    - TokenExpiredError: Истекший токен
    - AuthError: Ошибка аутентификации

Example:
    >>> raise TokenMissingError()
    >>> raise UserExistsError("email", "user@example.com")
"""

from .base import BaseAPIException


class TokenMissingError(BaseAPIException):
    """
    Исключение, которое вызывается, когда токен отсутствует.
    """

    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Токен отсутствует",
            error_type="token_missing",
            extra={},
        )


class InvalidCredentialsError(BaseAPIException):
    """
    Исключение, которое вызывается, когда указаны неверные учетные данные.
    """

    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Неверные учетные данные",
            error_type="invalid_credentials",
            extra={},
        )


class TokenExpiredError(BaseAPIException):
    """
    Исключение, которое вызывается, когда токен истек.
    """

    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Токен просрочен",
            error_type="token_expired",
            extra={},
        )


class AuthError(BaseAPIException):
    """
    Исключение, которое вызывается, когда пользователь не аутентифицирован.
    """

    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Неверные учетные данные, попробуйте снова",
            error_type="auth_error",
            extra={},
        )


class InvalidPasswordError(BaseAPIException):
    """
    Исключение при неверном пароле во время входа
    """

    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Неверный пароль",
            error_type="invalid_password",
            extra={},
        )

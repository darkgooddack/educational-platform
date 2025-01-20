"""
Исключения для аутентификации и управления пользователями.

1. Базовый класс AuthenticationError наследуется от BaseAPIException

2. Специфические исключения наследуются от AuthenticationError:
- InvalidCredentialsError - неверные учетные данные
- InvalidEmailFormatError - неверный формат email
- InvalidPasswordError - неверный пароль
- WeakPasswordError - слабый пароль

3. Отдельная ветка для работы с токенами:
- TokenError - базовый класс ошибок токена
- TokenMissingError - отсутствующий токен
- TokenExpiredError - истекший токен
"""

from ..base import BaseAPIException

class AuthenticationError(BaseAPIException):
    """Ошибка аутентификации"""
    def __init__(
        self,
        detail: str,
        error_type: str = "authentication_error",
        extra: dict = None
    ):
        super().__init__(
            status_code=401,
            detail=detail,
            error_type=error_type,
            extra=extra or {}
        )

class InvalidCredentialsError(AuthenticationError):
    """Неверные учетные данные"""

    def __init__(self):
        super().__init__(
            detail="🔐 Неверный email или пароль"
        )


class InvalidEmailFormatError(BaseAPIException):
    """
    Исключение, которое вызывается, когда формат email недействителен.

    Attributes:
        email (str): Недействительный email.
    """

    def __init__(self, email: str):
        super().__init__(
            status_code=400,
            detail=f"Неверный формат email: {email}",
            error_type="invalid_email_format",
            extra={"email": email},
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

class WeakPasswordError(BaseAPIException):
    """
    Исключение, которое вызывается, когда пароль является слабым.

    Attributes:
        password (str): Слабый пароль.
    """

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Пароль должен быть минимум 8 символов!",
            error_type="weak_password",
            extra={},
        )

class TokenError(AuthenticationError):
    """Базовая ошибка токена"""
    def __init__(
        self,
        detail: str,
        error_type: str = "token_error",
        extra: dict = None
    ):
        super().__init__(
            detail=detail,
            error_type=error_type,
            extra=extra or {"token_error": True}
        )

class TokenMissingError(TokenError):
    """Токен отсутствует"""
    def __init__(self):
        super().__init__(
            detail="Токен отсутствует",
            error_type="token_missing"
        )

class TokenExpiredError(TokenError):
    """Токен просрочен"""
    def __init__(self):
        super().__init__(
            detail="Токен просрочен",
            error_type="token_expired"
        )

from ..base import BaseAPIException

class AuthenticationError(BaseAPIException):
    """Базовый класс ошибок аутентификации"""
    def __init__(
        self,
        detail: str = "Ошибка аутентификации",
        error_type: str = "authentication_error",
        extra: dict = None
    ):
        super().__init__(
            status_code=401,
            detail=detail,
            error_type=error_type,
            extra=extra or {}
        )

class TokenError(AuthenticationError):
    """Базовый класс ошибок токена"""
    def __init__(
        self,
        detail: str,
        error_type: str = "token_error",
        extra: dict = None
    ):
        super().__init__(
            detail=detail,
            error_type=error_type,
            extra=extra or {"token": True}
        )

class TokenInvalidError(TokenError):
    """Невалидный токен"""
    def __init__(self):
        super().__init__(
            detail="Невалидный токен",
            error_type="token_invalid"
        )

class TokenExpiredError(TokenError):
    """Истекший токен"""
    def __init__(self):
        super().__init__(
            detail="Срок действия токена истек",
            error_type="token_expired"
        )

class TokenMissingError(TokenError):
    """Отсутствующий токен"""
    def __init__(self):
        super().__init__(
            detail="Токен отсутствует",
            error_type="token_missing"
        )

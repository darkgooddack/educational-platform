from app.core.exceptions.v1.base import BaseAPIException


class AIChatError(BaseAPIException):
    def __init__(
        self, message: str, error_type: str, status_code: int = 400, extra: dict = None
    ):
        super().__init__(
            status_code=status_code, detail=message, error_type=error_type, extra=extra
        )


class AIChatCompletionError(AIChatError):
    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            message=f"Ошибка при получении ответа от AI: {message}",
            error_type="ai_completion_error",
            status_code=500,
            extra=extra,
        )


class AIChatConfigError(AIChatError):
    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            message=f"Ошибка конфигурации AI: {message}",
            error_type="ai_config_error",
            status_code=500,
            extra=extra,
        )


class AIChatAuthError(AIChatError):
    def __init__(self, message: str = "Ошибка авторизации в API"):
        super().__init__(message=message, error_type="ai_auth_error", status_code=401)

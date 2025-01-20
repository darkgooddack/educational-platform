from ..base import BaseAPIException

class OAuthError(BaseAPIException):
    """Базовая ошибка OAuth"""
    def __init__(self, detail: str, extra: dict = None):
        super().__init__(
            status_code=401,
            detail=detail,
            error_type="oauth_error",
            extra=extra
        )

class InvalidProviderError(OAuthError):
    """Неподдерживаемый провайдер OAuth"""
    def __init__(self, provider: str):
        super().__init__(
            detail=f"Провайдер {provider} не поддерживается",
            extra={"provider": provider}
        )

class OAuthConfigError(OAuthError):
    """Ошибка конфигурации OAuth"""
    def __init__(self, provider: str, missing_fields: list):
        super().__init__(
            detail=f"Провайдер{provider}: Отсутствуют обязательные поля конфигурации: {', '.join(missing_fields)}",
            extra={"missing_fields": missing_fields}
        )

class OAuthTokenError(OAuthError):
    """Ошибка получения токена OAuth"""
    def __init__(self, provider: str, error: str):
        super().__init__(
            detail=f"Ошибка получения токена от {provider}: {error}",
            extra={"provider": provider, "error": error}
        )

class OAuthUserDataError(OAuthError):
    """Ошибка получения данных пользователя"""
    def __init__(self, provider: str, error: str):
        super().__init__(
            detail=f"Ошибка получения данных пользователя от {provider}: {error}",
            extra={"provider": provider, "error": error}
        )

class OAuthInvalidGrantError(OAuthError):
    """Ошибка невалидного или истекшего кода авторизации"""
    def __init__(self, provider: str):
        super().__init__(
            detail=f"Код авторизации от провайдера {provider} недействителен или истек. Пожалуйста, повторите вход.",
            extra={
                "provider": provider,
                "error_code": "invalid_grant",
                "requires_reauth": True
            }
        )
"""
Модуль обработки сообщений аутентификации.
"""

import logging

from app.core.exceptions import (InvalidEmailFormatError, UserExistsError,
                                 UserNotFoundError, WeakPasswordError)
from app.schemas import AuthSchema, TokenSchema
from app.services import AuthService

logger = logging.getLogger(__name__)


async def handle_authenticate(data: dict, auth_service: AuthService) -> dict:
    """
    Обрабатывает сообщение аутентификации.

    Args:
        data: Данные для аутентификации
        auth_service: Сервис аутентификации

    Returns:
        Токен доступа и тип токена
    """
    logger.info("🔐 Попытка аутентификации пользователя: %s", data.get("email"))
    try:
        auth_data_schema = AuthSchema(**data)
        token: TokenSchema = await auth_service.authenticate(auth_data_schema)
        logger.info("✅ Пользователь %s успешно аутентифицирован", data.get("email"))
        return {
            "status_code": 200,
            "access_token": token.access_token,
            "token_type": token.token_type,
        }

    except (
        UserNotFoundError,
        UserExistsError,
        InvalidEmailFormatError,
        WeakPasswordError,
    ) as e:
        logger.error("❌ Ошибка аутентификации: %s", str(e))
        return {
            "status_code": getattr(e, "status_code", 400),
            "detail": str(e),
            "error_type": getattr(e, "error_type", "validation_error"),
            "extra": getattr(e, "extra", {}),
        }


async def handle_logout(token: str, auth_service: AuthService) -> dict:
    """
    Обрабатывает сообщение выхода.

    Args:
        token: Токен для выхода
        auth_service: Сервис аутентификации

    Returns:
        Сообщение об успешном выходе
    """
    logger.info("🚪 Попытка выхода пользователя")
    try:
        result = await auth_service.logout(token)
        logger.info("✅ Пользователь успешно вышел")
        return result
    except Exception as e:
        logger.error("❌ Ошибка при выходе: %s", str(e))
        return {"status_code": 500, "detail": str(e)}

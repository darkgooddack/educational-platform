"""
Модуль обработки регистрации пользователя.
"""

import logging

from pydantic_core import ValidationError

from app.core.exceptions import (InvalidEmailFormatError, UserExistsError,
                                 WeakPasswordError)
from app.schemas import RegistrationSchema
from app.services import UserService

logger = logging.getLogger(__name__)


async def handle_register(data: dict, user_service: UserService) -> dict:
    """
    Обрабатывает сообщение регистрации.

    Args:
        data: Данные пользователя для регистрации
        user_service: Сервис пользователей
        auth_service: Сервис аутентификации

    Returns:
        Токен доступа и тип токена
    """
    logger.info("📝 Попытка регистрации пользователя: %s", data.get("email"))
    try:
        user_data_schema = RegistrationSchema(**data)
        user = await user_service.create_user(user_data_schema)
        logger.info("✅ Пользователь %s успешно зарегистрирован", user.email)
        return {"status_code": 201, "user_id": str(user.user_id), "email": user.email}

    except (
        ValidationError,
        UserExistsError,
        InvalidEmailFormatError,
        WeakPasswordError,
    ) as e:
        logger.error("❌ Ошибка регистрации: %s", str(e))
        return {
            "status_code": getattr(e, "status_code", 400),
            "detail": str(e),
            "error_type": getattr(e, "error_type", "validation_error"),
            "extra": getattr(e, "extra", {}),
        }

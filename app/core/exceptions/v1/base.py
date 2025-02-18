"""
Базовый класс для обработки исключений app.

Включает в себя:
- Логирование ошибок.
- Формирование ответа с ошибкой.
- Генерация уникального идентификатора для ошибки.
- Преобразование даты и времени в формат ISO 8601 с учетом часового пояса.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import pytz
from fastapi import HTTPException

logger = logging.getLogger(__name__)
moscow_tz = pytz.timezone("Europe/Moscow")


class BaseAPIException(HTTPException):
    """
    Базовый класс для обработки исключений app.

    Attributes:
        status_code: Код статуса HTTP.
        detail: Сообщение об ошибке.
        error_type: Тип ошибки.
        extra: Дополнительные данные для контекста.

    Raises:
        HTTPException: Исключение с указанным статусом и сообщением.

    Returns:
        None
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: str,
        extra: Optional[Dict[Any, Any]] = None,
    ) -> None:

        self.error_type = error_type  # Сохраняем error_type
        self.extra = extra or {}  # Сохраняем extra

        context = {
            "timestamp": datetime.now(moscow_tz).isoformat(),
            "request_id": str(uuid.uuid4()),
            "status_code": status_code,
            "error_type": error_type,
            **(extra or {}),
        }

        logger.error(detail, extra=context)
        super().__init__(status_code=status_code, detail=detail)


class DatabaseError(BaseAPIException):
    """
    Ошибка при работе с базой данных.
    """

    def __init__(self, message: str, extra: Optional[Dict[Any, Any]] = None):
        super().__init__(
            status_code=500,
            detail=f"Ошибка базы данных: {message}",
            error_type="database_error",
            extra=extra,
        )


class ValueNotFoundError(BaseAPIException):
    """
    Значение поля не найдено.

    Attributes:
        field (str): наименование поля.
        value (str): значение поля.
    """

    def __init__(self, field: str, value: str):

        super().__init__(
            status_code=404,
            detail=f"Поле {field} со значением '{value}' не существует!",
            error_type="user_not_found",
            extra={"user_" + field: value},
        )

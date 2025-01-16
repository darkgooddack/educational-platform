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

import pytz
from fastapi import HTTPException

# logger =logging.getLogger(__name__)
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
        self, status_code: int, detail: str, error_type: str, extra: dict = None
    ) -> None:

        context = {
            "timestamp": datetime.now(moscow_tz).isoformat(),
            "request_id": str(uuid.uuid4()),
            "status_code": status_code,
            "error_type": error_type,
            **(extra or {}),
        }

        # logger.error(detail, extra=context)
        super().__init__(status_code=status_code, detail=detail)

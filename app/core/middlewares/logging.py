"""
Модуль логирования HTTP запросов в API Gateway.

Предоставляет middleware для автоматического логирования входящих запросов
с разным уровнем детализации в зависимости от настроек.

Components:
    - LoggingMiddleware: Middleware класс для перехвата и логирования запросов
    - Обработка исключений с конвертацией в JSON ответы

Levels of logging:
    - DEBUG: логируются пути запросов и все HTTP заголовки
    - INFO и выше: логируются только пути запросов

Usage:
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

Dependencies:
    - FastAPI/Starlette для обработки HTTP
    - logging для работы с логами
    - app.core.config для конфигурации
    - app.core.exceptions для обработки ошибок
"""

import logging

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import config
from app.core.exceptions import BaseAPIException

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Мидлвара для логирования запросов.

    Если уровень логирования DEBUG, то логируются пути и заголовки запроса,
    иначе если не DEBUG, то логируется только путь запроса.

    Attributes:
        request: Request - запрос
        call_next: callable - функция для вызова следующего мидлвари

    Returns:
        response: Response - ответ

    Raises:
        BaseAPIException: базовое исключение API
        HTTPException: HTTP исключение
    """

    async def dispatch(self, request: Request, call_next):
        """
        Метод для обработки запроса.

        Args:
            request: Request - запрос
            call_next: callable - функция для вызова следующего мидлвари

        Returns:
            response: Response - ответ

        Raises:
            BaseAPIException: базовое исключение API
            HTTPException: HTTP исключение
        """
        if getattr(config, "logging_level", "INFO") == "DEBUG":
            logger.debug("Request path: %s", request.url.path)
            logger.debug("Headers: %s", request.headers)

        try:
            response = await call_next(request)
            return response
        except BaseAPIException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code, content={"detail": str(e.detail)}
            )

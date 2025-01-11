import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from api.errors.v1.users import BaseAPIException
from api.core.config import env_config

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Мидлвара для логирования запросов.

    Если уровень логирования DEBUG, то логируются пути и заголовки запроса,
    иначе если не DEBUG, то логируется только путь запроса.

    Args:
        request: Request - запрос
        call_next: callable - функция для вызова следующего мидлвари

    Returns:
        response: Response - ответ

    Raises:
        BaseAPIException: базовое исключение API
        HTTPException: HTTP исключение
    """

    async def dispatch(self, request: Request, call_next):
        if env_config.logging_level == "DEBUG":
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

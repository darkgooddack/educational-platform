from datetime import datetime

import pytz
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException

from app.core.exceptions import BaseAPIException

moscow_tz = pytz.timezone("Europe/Moscow")


# Обработчик для кастомных исключений
async def api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": exc.error_type,
            "extra": exc.extra,
            "timestamp": datetime.now(moscow_tz).isoformat(),
        },
    )


# Базовый HTTP обработчик
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": str(exc.detail),
            "error_type": "http_error",
            "status_code": exc.status_code,
            "timestamp": datetime.now(moscow_tz).isoformat(),
        },
    )


# Обработчик ошибок валидации
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Ошибка валидации данных",
            "error_type": "validation_error",
            "errors": [{"loc": err["loc"], "msg": err["msg"]} for err in exc.errors()],
            "timestamp": datetime.now(moscow_tz).isoformat(),
        },
    )


# Обработчик WebSocket исключений
async def websocket_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Ошибка WebSocket соединения",
            "error_type": "websocket_error",
            "error": str(exc),
            "timestamp": datetime.now(moscow_tz).isoformat(),
        },
    )


# Обработчик ошибок авторизации
async def auth_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": "Ошибка авторизации",
            "error_type": "auth_error",
            "error": str(exc),
            "timestamp": datetime.now(moscow_tz).isoformat(),
        },
    )


# Общий обработчик непредвиденных ошибок
async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Внутренняя ошибка сервера",
            "error_type": "internal_error",
            "error": str(exc),
            "timestamp": datetime.now(moscow_tz).isoformat(),
        },
    )

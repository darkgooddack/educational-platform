import asyncio
import socket
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response
from sqlalchemy import text
from registration_service.api.core.database.session import get_db_session
from registration_service.api.core.config import app_config

router = APIRouter(**app_config.SERVICES["health"].to_dict())


@router.get("/", status_code=204)
async def health(session: AsyncSession = Depends(get_db_session)):
    """
    Проверка работоспособности сервиса.

    Выполняет:
    1. Проверку подключения к базе данных через простой SELECT запрос
    2. Проверку таймаута соединения (1 секунда)

    Returns:
        204: Сервис работает нормально
        503: Проблемы с БД или таймаут соединения
    """
    try:
        # Пробуем выполнить простой запрос с таймаутом в 1 секунду
        await asyncio.wait_for(
            session.execute(text("SELECT 1")),
            timeout=1
        )
    except (asyncio.TimeoutError, socket.gaierror):
        # Если таймаут или ошибка сети - возвращаем 503 Service Unavailable
        return Response(status_code=503)
    # Всё ок - возвращаем 204 No Content
    return Response(status_code=204)
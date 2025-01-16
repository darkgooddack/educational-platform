"""
Обработчик для проверки работоспособности сервиса.

Функция handle_health_check проверяет работоспособность сервиса,
проверяя соединение с базой данных. Если соединение успешно установлено,
то отправляется ответ "healthy". В случае возникновения ошибки,
отправляется ответ "unhealthy" с соответствующим сообщением об ошибке.
"""

import logging

from aio_pika import IncomingMessage
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.exc import TimeoutError as SQLATimeoutError

from app.core.dependencies.database import SessionContextManager

from .utils import send_response

logger = logging.getLogger(__name__)


async def handle_health_check(message: IncomingMessage) -> None:
    """
    Проверяет работоспособность сервиса.

    Args:
        message: Входящее сообщение

    Returns: None
    """
    try:
        async with SessionContextManager() as session_manager:

            logger.info("🔍 Проверяю БД...")
            await session_manager.session.execute(text("SELECT 1"))

            logger.info("✅ БД работает, отправляю healthy")
            await send_response(message, {"status": "healthy"})

    except SQLATimeoutError as e:
        logger.error("⏰ Таймаут подключения к БД: %s", str(e))
        await send_response(message, {"status": "unhealthy", "error": "timeout"})

    except DBAPIError as e:
        logger.error("🔌 Ошибка подключения к БД: %s", str(e))
        await send_response(message, {"status": "unhealthy", "error": "connection"})

    except SQLAlchemyError as e:
        logger.error("💀 Ошибка SQLAlchemy: %s", str(e))
        await send_response(message, {"status": "unhealthy", "error": "database"})

    except Exception as e:
        logger.error("🚨 Неизвестная ошибка: %s", str(e))
        await send_response(message, {"status": "unhealthy", "error": "unknown"})

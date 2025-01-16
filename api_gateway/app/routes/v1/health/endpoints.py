"""
Модуль для проверки здоровья сервисов.

Этот модуль содержит эндпоинт для:
- Проверки доступности всех микросервисов
- Проверки соединений с Redis и RabbitMQ
"""

from aio_pika import Connection
from fastapi import APIRouter, Depends
from starlette.responses import Response

from app.core.config import config
from app.core.dependencies import get_rabbitmq, get_redis
from app.core.rabbit.producer import check_service_health

router = APIRouter(**config.SERVICES["health"].to_dict())


@router.get("/", status_code=204)
async def health_check(
    redis=Depends(get_redis), rabbitmq: Connection = Depends(get_rabbitmq)
) -> Response:
    """
    Проверяет здоровье всех сервисов.

    Args:
        redis: Redis клиент для проверки соединения
        rabbitmq: RabbitMQ соединение для проверки микросервисов

    Returns:
        Response: 204 если все сервисы живы, 503 если есть проблемы
    """
    try:
        # Проверяем Redis
        redis.ping()

        # Проверяем микросервисы через RabbitMQ
        async with rabbitmq.channel() as channel:
            is_healthy = await check_service_health(channel)
            if not is_healthy:
                return Response(status_code=503)

            return Response(status_code=204)
    except:
        return Response(status_code=503)

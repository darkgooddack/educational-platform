"""
Модуль для проверки здоровья сервисов.

Этот модуль содержит эндпоинт для:
- Проверки доступности всех микросервисов
- Проверки соединений с Redis и RabbitMQ
"""
import logging
from aio_pika import Connection
from fastapi import APIRouter, Depends
from starlette.responses import Response

from app.core.config import config
from app.core.dependencies import get_rabbitmq, get_redis
from app.core.messaging.health import HealthMessageProducer

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
        redis.ping()

        async with rabbitmq.channel() as channel:
            producer = HealthMessageProducer(channel)

            if not await producer.check_health():
                logging.error("Ошибка проверки здоровья")
                return Response(status_code=503)
            return Response(status_code=204)
    except Exception as e:
        logging.error(f"Ошибка проверки здоровья: {e}")
        return Response(status_code=503)
            

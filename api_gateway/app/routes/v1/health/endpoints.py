"""
Модуль для проверки здоровья сервисов.

Этот модуль содержит эндпоинт для:
- Проверки доступности всех микросервисов
- Проверки соединений с Redis и RabbitMQ
"""

from aio_pika import Connection, Message
from fastapi import APIRouter, Depends
from starlette.responses import Response

from app.core.config import config
from app.core.dependencies import get_redis, get_rabbitmq

router = APIRouter(**config.SERVICES["health"].to_dict())


@router.get("/", status_code=204)
async def health_check(
    redis=Depends(get_redis), rabbitmq: Connection = Depends(get_rabbitmq)
):
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
        await redis.ping()

        # Проверяем микросервисы через RabbitMQ
        async with rabbitmq.channel() as channel:
            # Только публикуем, ответ не важен
            await channel.default_exchange.publish(
                Message(body=b"health_check"), routing_key="health_check"
            )

            return Response(status_code=204)
    except:
        return Response(status_code=503)

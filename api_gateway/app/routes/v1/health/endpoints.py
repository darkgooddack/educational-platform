"""
Модуль для проверки здоровья сервисов.

Этот модуль содержит эндпоинт для:
- Проверки доступности всех микросервисов
- Проверки соединений с Redis и RabbitMQ

TODO:
Разделение проверок Redis и сервисов
Enum для статус кодов
Более подробное логирование
Типизация возвращаемых значений
Чистая структура кода
"""
import logging
from aio_pika import Connection
from fastapi import APIRouter, Depends
from starlette.responses import Response

from app.core.config import config
from app.core.dependencies import get_rabbitmq, get_redis
from app.core.messaging.health import HealthMessageProducer, HealthStatus

# logger =logging.getLogger(__name__)

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

            is_healthy, status = await producer.check_health()

            if is_healthy:
                return Response(status_code=204)  # Все ок

            # Иначе обрабатываем ошибки
            logging.warning(f"Health check failed with status: {status.value}")
            if status in [HealthStatus.TIMEOUT, HealthStatus.CONNECTION_ERROR]:
                return Response(status_code=503)
            return Response(status_code=500)
        
    except Exception as e:
        # logger.error(f"Critical health check error: {e}")
        return Response(status_code=500)
            

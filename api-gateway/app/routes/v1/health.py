"""
Модуль для проверки здоровья сервисов.

Этот модуль содержит эндпоинт для:
- Проверки доступности всех микросервисов
- Проверки соединений с Redis и RabbitMQ
"""

from aio_pika import Connection
from fastapi import APIRouter, Depends
from starlette.responses import Response

from app.core.dependencies import get_rabbitmq, get_redis
from app.schemas.v1.health import HealthStatusCodes
from app.services.v1.health import HealthService

health_service = HealthService()


def setup_routes(router: APIRouter):
    """
    Настройка маршрутов для проверки здоровья сервисов.

    Args:
        router (APIRouter): Объект APIRouter.

    Routes:
        GET /health: Проверка доступности всех микросервисов
    """
    @router.get("/", status_code=HealthStatusCodes.OK.value)
    async def health_check(
        redis=Depends(get_redis),
        rabbitmq: Connection = Depends(get_rabbitmq),
    ) -> Response:
        """
        🏥 **Проверка доступности всех микросервисов.**
        
        **Args**:
        - **redis**: Объект Redis
        - **rabbitmq**: Объект RabbitMQ

        **Returns**:
        - **Response**: Статус проверки здоровья
        """
        return await health_service.check_health(redis, rabbitmq)

"""
Модуль для работы с сервисом здоровья
"""

import logging
from typing import Tuple

from aio_pika import Connection
from starlette.responses import Response

from app.core.messaging.health import HealthMessageProducer
from app.schemas.v1.health import HealthStatusCodes

logger = logging.getLogger(__name__)


class HealthService:
    """
    Сервис для проверки здоровья системы.

    Attributes:
        redis (Redis): Объект Redis для проверки его работоспособности.

    Methods:
        check_redis(redis) -> Tuple[bool, str]: Проверка работоспособности Redis
        check_services(rabbitmq: Connection) -> Tuple[bool, str]: Проверка работоспособности микросервисов
        check_health(redis, rabbitmq: Connection) -> Response: Общая проверка работоспособности системы
    """

    async def check_redis(self, redis) -> Tuple[bool, str]:
        """
        Проверка работоспособности Redis

        Args:
            redis (Redis): Объект Redis для проверки его работоспособности.

        Returns:
            Tuple[bool, str]: Результат проверки и сообщение об ошибке (если есть).
        """
        try:
            redis.ping()
            logger.info("✅ Проверка Redis пройдена")
            return True, "Redis работает"
        except Exception as e:
            logger.error("❌ Проверка Redis провалена: %s", str(e))
            return False, f"Ошибка Redis: {str(e)}"

    async def check_services(self, rabbitmq: Connection) -> Tuple[bool, str]:
        """
        Проверка работоспособности микросервисов

        Args:
            rabbitmq (Connection): Объект RabbitMQ для проверки его работоспособности.

        Returns:
            Tuple[bool, str]: Результат проверки и сообщение об ошибке (если есть).
        """
        try:
            async with rabbitmq.channel() as channel:
                producer = HealthMessageProducer(channel)
                is_healthy, status = await producer.check_health()

                if is_healthy:
                    logger.info("✅ Проверка сервисов пройдена")
                    return True, "Сервисы работают"

                logger.warning("❌ Проверка сервисов провалена: %s", status.value)
                return False, f"Ошибка сервисов: {status.value}"
        except Exception as e:
            logger.error("💀 Проверка сервисов провалена: %s", str(e))
            return False, f"Ошибка сервисов: {str(e)}"

    async def check_health(self, redis, rabbitmq: Connection) -> Response:
        """
        Общая проверка работоспособности системы

        Args:
            redis (Redis): Объект Redis для проверки его работоспособности.
            rabbitmq (Connection): Объект RabbitMQ для проверки его работоспособности.

        Returns:
            Response: Статус проверки здоровья.
        """
        redis_ok, redis_msg = await self.check_redis(redis)
        services_ok, services_msg = await self.check_services(rabbitmq)

        if redis_ok and services_ok:
            return Response(status_code=HealthStatusCodes.OK.value)

        logger.error(
            "🚨 Проверка здоровья провалена: Redis: %s, Сервисы: %s",
            redis_msg,
            services_msg,
        )
        return Response(
            status_code=(
                HealthStatusCodes.SERVICE_UNAVAILABLE.value
                if "timeout" in services_msg or "connection" in services_msg
                else HealthStatusCodes.INTERNAL_ERROR.value
            )
        )

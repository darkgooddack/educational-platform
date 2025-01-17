"""
Модуль для отправки сообщений о здоровье сервисов.

Модуль содержит класс HealthMessageProducer,
который наследуется от MessageProducer и отвечает за отправку сообщений
о здоровье сервисов.
"""

import logging
from typing import Tuple

from aio_pika.exceptions import AMQPChannelError, AMQPConnectionError

from app.schemas.v1.health import HealthStatus

from .producer import MessageProducer

logger = logging.getLogger(__name__)


class HealthMessageProducer(MessageProducer):
    """
    Производитель сообщений для проверки здоровья сервисов.
    """

    async def check_health(self) -> Tuple[bool, HealthStatus]:
        """
        Проверяет здоровье сервисов через RabbitMQ.

        Returns:
            bool: True если все сервисы здоровы, False при любой ошибке или таймауте

        Note:
            Отправляет сообщение с routing_key='health_check' и ждет ответ {'status': 'healthy'}
        """
        try:
            response, error = await self.send_and_wait(
                routing_key="health_check", message={"status": "check"}
            )

            logger.info("🔍 Получил ответ: %s, ошибка: %s", response, error)

            if error:
                return False, HealthStatus(error)

            status = response.get("status") == "healthy"

            logger.info(
                "💉 Статус health check: %s", "✅ HEALTHY" if status else "❌ UNHEALTHY"
            )

            return status, (
                HealthStatus.HEALTHY if status else HealthStatus.UNKNOWN_ERROR
            )

        except AMQPConnectionError as e:
            logger.error("🔌 Ошибка подключения RabbitMQ: %s", str(e))
            return False, HealthStatus.CONNECTION_ERROR

        except AMQPChannelError as e:
            logger.error("📡 Ошибка канала RabbitMQ: %s", str(e))
            return False, HealthStatus.CONNECTION_ERROR

        except TimeoutError:
            logger.error("⏰ Таймаут при проверке health")
            return False, HealthStatus.TIMEOUT

        except Exception as e:
            logger.error("💀 Неизвестная ошибка при проверке health: %s", str(e))
            return False, HealthStatus.UNKNOWN_ERROR

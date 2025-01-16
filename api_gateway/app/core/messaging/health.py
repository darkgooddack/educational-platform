from enum import Enum
from typing import Tuple
from .base import MessageProducer

class HealthStatus(Enum):
    HEALTHY = "healthy"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection"
    UNKNOWN_ERROR = "unknown"

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
                routing_key="health_check", 
                message={"status": "check"}
            )

            if error:
                return False, HealthStatus(error)
            
            return response.get("status") == "healthy", HealthStatus.HEALTHY
        
        except Exception:
            return False, HealthStatus.UNKNOWN_ERROR

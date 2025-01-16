import logging
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
            logging.info(f"Получил ответ: {response}, ошибка: {error}")
            if error:
                return False, HealthStatus(error)
            
            status = response.get("status") == "healthy"
            logging.info(f"Статус health check: {status}")
            return status, HealthStatus.HEALTHY if status else HealthStatus.UNKNOWN_ERROR
        
        except Exception as e:
            logging.error(f"Ошибка при проверке health: {str(e)}")
            return False, HealthStatus.UNKNOWN_ERROR

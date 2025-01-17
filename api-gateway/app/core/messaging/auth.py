"""
Продюсер для отправки сообщений аутентификации в auth сервис.
"""

from typing import Optional, Tuple

from app.schemas.v1.auth import AuthAction

from .producer import MessageProducer


class AuthMessageProducer(MessageProducer):
    """
    Продюсер для отправки сообщений аутентификации в RabbitMQ для аутентификации.

     Attributes:
         channel (Channel): Канал RabbitMQ для коммуникации

     TODO:
     - Добавить метрики:
         - Счетчик успешных/неуспешных аутентификаций
         - Время ответа auth сервиса
         - Количество повторных попыток
         - Типы возникающих ошибок
     - Добавить логирование всех этапов отправки
     - Реализовать Circuit Breaker для отказоустойчивости
     - Добавить валидацию входящих данных
     - Добавить тайм-ауты для разных типов действий
     - Реализовать очередь для повторной обработки
     - Добавить мониторинг состояния очереди
    """

    async def send_auth_message(
        self, action: AuthAction, data: dict
    ) -> Tuple[dict, Optional[str]]:
        """
        Отправка сообщения в RabbitMQ для аутентификации

        Args:
            action: Действие для отправки сообщения
            data: Данные для отправки

        Returns:
            Tuple[dict, Optional[str]]: Ответ от RabbitMQ и тип ошибки
        """
        message = {"action": action.value, "data": data}
        return await self.send_and_wait(routing_key="auth_queue", message=message)

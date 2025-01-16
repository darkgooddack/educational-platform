"""
Продюсер для отправки сообщений аутентификации в RabbitMQ.
"""

from typing import Optional, Tuple

from app.schemas.v1.authentication import AuthAction

from .producer import MessageProducer


class AuthMessageProducer(MessageProducer):
    """
    Продюсер для отправки сообщений аутентификации в RabbitMQ.

    Attributes:
        channel (Channel): Канал RabbitMQ

    TODO:
    - Метрики:
        - Счетчики успешных/неуспешных операций
        - Время ответа
        - Количество ретраев
        - Типы ошибок
    - Логирование этапов
    - Circuit Breaker
    - Валидация данных
    - Тайм-ауты по типам
    - Очередь повторной обработки
    - Мониторинг очереди
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
            Tuple[dict, Optional[str]]: Ответ от сервиса и тип ошибки
        """
        message = {"action": action.value, "data": data}
        return await self.send_and_wait(routing_key="auth_queue", message=message)

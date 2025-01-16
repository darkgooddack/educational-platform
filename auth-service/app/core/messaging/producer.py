"""
Базовый класс для отправки сообщений в RabbitMQ.
"""

import json
import logging
import time
from typing import Optional

from aio_pika import Channel, Message
from tenacity import retry, stop_after_attempt, wait_exponential


class MessageProducer:
    """
    Базовый класс для отправки сообщений в RabbitMQ.

    Attributes:
        channel (Channel): Канал RabbitMQ для коммуникации
    """

    def __init__(self, channel: Channel) -> None:
        self.channel = channel
        self.MESSAGE_EXPIRATION = 60000  # 60 секунд на жизнь сообщения
        self.RESPONSE_TIMEOUT = 30  # 30 секунд на ожидание ответа
        self.logger = logging.getLogger(__name__)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        before_sleep=lambda retry_state: logging.warning(
            "🔄 Попытка %d провалилась, повторяю через %d секунд...",
            retry_state.attempt_number,
            retry_state.next_action.sleep,
        ),
    )
    async def send_and_wait(
        self, routing_key: str, message: dict
    ) -> tuple[dict, Optional[str]]:
        """
        Отправляет сообщение и ждет ответ.

        Args:
            routing_key: Ключ маршрутизации для сообщения
            message: Сообщение для отправки

        Returns:
            dict: Ответ от получателя или {'error': 'Timeout'} при таймауте

        Note:
            Таймаут установлен на 30 секунд


        """
        start_time = time.time()

        queue = await self.channel.declare_queue("", exclusive=True)

        self.logger.debug(
            "📨 Отправка сообщения в очередь %s: %s", routing_key, message
        )

        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(message).encode(),
                reply_to=queue.name,
                expiration=self.MESSAGE_EXPIRATION,
            ),
            routing_key=routing_key,
        )

        try:
            self.logger.debug("⏳ Ожидание ответа из очереди %s", queue.name)
            async with queue.iterator(timeout=self.RESPONSE_TIMEOUT) as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        response = json.loads(message.body.decode())
                        self.logger.debug(
                            "✅ Получен ответ:\n"
                            "├─ Статус: %s\n"
                            "├─ Данные: %s\n"
                            "└─ Время обработки: %sms",
                            response.get("status", "OK"),
                            json.dumps(response, indent=2, ensure_ascii=False),
                            round((time.time() - start_time) * 1000),
                        )
                        return response, None

        except TimeoutError:
            self.logger.error("⏰ Таймаут ожидания ответа из очереди %s", queue.name)
            return {"error": "Timeout"}, "timeout"

        except ConnectionError:
            self.logger.error("🔌 Ошибка подключения к RabbitMQ")
            return {"error": "Connection failed"}, "connection"

        except Exception as e:
            self.logger.error("💀 Неизвестная ошибка: %s", str(e))
            return {"error": str(e)}, "unknown"

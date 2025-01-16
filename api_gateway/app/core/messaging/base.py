from typing import Optional
import json
from aio_pika import Message, Channel
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
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def send_and_wait(self, routing_key: str, message: dict) -> tuple[dict, Optional[str]]:
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
        queue = await self.channel.declare_queue("", exclusive=True)
        
        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(message).encode(),
                reply_to=queue.name,
                expiration=self.MESSAGE_EXPIRATION
                ),
                routing_key=routing_key,
        )
        

        try:
            async with queue.iterator(timeout=self.RESPONSE_TIMEOUT) as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        return json.loads(message.body.decode()), None
        except TimeoutError:
            return {"error": "Timeout"}, "timeout"
        except ConnectionError:
            return {"error": "Connection failed"}, "connection"
        except Exception as e:
            return {"error": str(e)}, "unknown"

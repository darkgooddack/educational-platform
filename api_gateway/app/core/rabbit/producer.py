import json
import asyncio
from aio_pika import Message


async def send_auth_message(channel, action: str, data: dict) -> dict:
    """
    Отправляет сообщение в auth_queue и ждет ответ

    Args:
        channel: RabbitMQ канал
        action: Действие, которое нужно выполнить
        data: Данные для действия

    Returns:
        dict: Ответ от auth_service
    """
    queue = await channel.declare_queue("", exclusive=True)

    message = {
        "action": action,
        "data": data
    }

    await channel.default_exchange.publish(
        Message(
            body=json.dumps(message).encode(),
            reply_to=queue.name,
            expiration=30000
        ),
        routing_key="auth_queue"
    )

    # Ждем ответ
    async with queue.iterator(timeout=30) as queue_iter:
        async for message in queue_iter:
            async with message.process():
                return json.loads(message.body.decode())

    return {"error": "Timeout"}

async def check_service_health(channel) -> bool:
    """
    Отправляет health check сообщение и ждет ответ

    Args:
        channel: RabbitMQ канал

    Returns:
        bool: True если сервис жив, False если нет ответа или ошибка
    """
    for _ in range(3):  # 3 попытки
        try:
            response_queue = await channel.declare_queue("", exclusive=True)

            # Отправляем пинг
            await channel.default_exchange.publish(
                Message(
                    body=b"health_check",
                    reply_to=response_queue.name,
                    expiration=5
                ),
                routing_key="health_check"
            )

            # Ждем ответ с таймаутом

            async with asyncio.timeout(3):
                async with response_queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            response = json.loads(message.body.decode())
                            return response["status"] == "healthy"

        except Exception:
            await asyncio.sleep(1)  # Ждем секунду между попытками

    return False

"""
Модуль проверки здоровья сервиса через RabbitMQ.

Когда API Gateway проверяет здоровье сервисов:
1. API Gateway отправляет сообщение в очередь health_check
2. Auth Service получает это сообщение
3. Если Auth Service жив - он подтверждает получение сообщения
4. API Gateway видит подтверждение и понимает что сервис жив
"""
from aio_pika import IncomingMessage
from fastapi import FastAPI

async def setup_health_check(_app: FastAPI, channel):
    """
    Настраивает обработчик health check сообщений.

    Args:
        app: FastAPI приложение
        channel: Канал RabbitMQ для работы с очередями

    Создает очередь health_check и подписывается на сообщения.
    При получении сообщения просто подтверждает его получение,
    сигнализируя что сервис жив.
    """
    async def health_callback(message: IncomingMessage):
        async with message.process():
            # Подтверждаем получение = сервис жив
            return

    # Создаем очередь и подписываемся
    queue = await channel.declare_queue("health_check", auto_delete=True)
    await queue.consume(health_callback)

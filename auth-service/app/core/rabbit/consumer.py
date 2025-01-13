"""
Модуль для обработки сообщений из RabbitMQ.

Обрабатывает команды:
- authenticate: аутентификация пользователя
- logout: выход из системы
- health_check: проверка работоспособности
"""

import json

from aio_pika import IncomingMessage, connect_robust

from app.core.config import config
from app.services import AuthenticationService


async def process_auth_message(
    message: IncomingMessage, auth_service: AuthenticationService
) -> None:
    """
    Обрабатывает сообщения аутентификации.

    Args:
        message: Входящее сообщение из RabbitMQ
        auth_service: Сервис аутентификации

    Message format:
        {
            "action": "authenticate" | "logout",
            "data": {...} | "token": "..."
        }
    """
    async with message.process():
        result = None
        body = json.loads(message.body.decode())
        action = body.get("action")

        if action == "authenticate":
            result = await auth_service.authenticate(body["data"])
        elif action == "logout":
            result = await auth_service.logout(body["token"])

        # Отправляем ответ
        await message.reply(json.dumps(result).encode())


async def start_consuming():
    """
    Запускает обработку очередей RabbitMQ.

    Слушает очереди:
    - auth_queue: команды аутентификации
    - health_check: проверка работоспособности
    """
    connection = await connect_robust(**config.rabbitmq_params)
    channel = await connection.channel()

    # Очереди для обработки
    auth_queue = await channel.declare_queue("auth_queue")
    health_queue = await channel.declare_queue("health_check")

    await auth_queue.consume(process_auth_message)
    await health_queue.consume(lambda x: x.ack())

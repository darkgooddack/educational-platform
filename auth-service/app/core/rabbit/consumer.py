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
from app.services import AuthenticationService, UserService
from app.core.dependencies.database import SessionContextManager
from .handlers import (
    handle_authenticate,
    handle_logout,
    handle_oauth,
    handle_register,
    handle_health_check,
    send_response
)

async def process_auth_message(
    message: IncomingMessage,
    auth_service: AuthenticationService,
    user_service: UserService
) -> None:
    """
    Процессинг сообщения из RabbitMQ.

    Args:
        message: Сообщение из RabbitMQ
        auth_service: Сервис аутентификации
        user_service: Сервис пользователей

    Message format:
        {
            "action": "authenticate",
            "data": {
                "email": "user@example.com",
                "password": "password123"
            }
        }
        {
            "action": "logout",
            "token": "your_access_token"
        }
        {
            "action": "oauth_authenticate",
            "provider": "google",
            "user_data": {
                "email": "user@example.com",
                "name": "John Doe"
            }
        }
        {
            "action": "register",
            "data": {
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "A.",
                "email": "user@example.com",
                "phone": "1234567890",
                "password": "password123"
            }
        }
    """
    body = json.loads(message.body.decode())
    action = body.get("action")

    handlers = {
        "authenticate": lambda: handle_authenticate(body.get("data"), auth_service),
        "logout": lambda: handle_logout(body.get("data", {}).get("token"), auth_service),
        "oauth_authenticate": lambda: handle_oauth(body["provider"], body["user_data"], auth_service),
        "register": lambda: handle_register(body["data"], user_service)
    }

    handler = handlers.get(action)


    if not handler:
        await send_response(message, {"error": f"Неизвестный action: {action}"})
    else:
        result = await handler()
        await send_response(message, result)
        


async def start_consuming():
    """
    Запускает обработку очередей RabbitMQ.

    Слушает очереди:
    - auth_queue: команды аутентификации
    - health_check: проверка работоспособности
    """

    async with SessionContextManager() as session_manager:
        # Создаем сервис аутентификации с сессией из контекстного менеджера
        auth_service = AuthenticationService(session_manager.session)
        user_service = UserService(session_manager.session)

    connection = await connect_robust(**config.rabbitmq_params)
    channel = await connection.channel()

    # Очереди для обработки
    queues = {
        "auth_queue": lambda msg: process_auth_message(msg, auth_service, user_service),
        "health_check": handle_health_check
    }

    for queue_name, handler in queues.items():
        queue = await channel.declare_queue(queue_name, auto_delete=True)
        await queue.consume(handler)

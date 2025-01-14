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
from app.schemas import TokenSchema
from app.core.dependencies.database import SessionContextManager

async def process_auth_message(
    message: IncomingMessage, 
    auth_service: AuthenticationService,
    user_service: UserService
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
        elif action == "oauth_authenticate":
            result = await auth_service.oauth_authenticate(
                body["provider"],
                body["user_data"]
            )
        elif action == "register":
            # Используем UserService для регистрации
            user = await user_service.create_user(body["data"])
            # Генерируем токен через AuthService
            payload = auth_service.create_payload(user)
            token = auth_service.generate_token(payload)
            await auth_service._data_manager.save_token(user, token)
            result = TokenSchema(access_token=token, token_type=config.token_type)

        # Отправляем ответ
        await message.reply(json.dumps(result).encode())


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
    auth_queue = await channel.declare_queue("auth_queue")
    health_queue = await channel.declare_queue(
        "health_check",
        auto_delete=False
    )

    await auth_queue.consume(lambda message: process_auth_message(message, auth_service, user_service))
    await health_queue.consume(lambda x: x.ack())
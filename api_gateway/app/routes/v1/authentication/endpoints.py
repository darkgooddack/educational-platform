"""
Модуль для обработки аутентификации и авторизации.

Этот модуль содержит эндпоинты для:
- Аутентификации пользователей
- Выхода из системы
"""

import json

from aio_pika import Connection, Message
from fastapi import APIRouter, Depends

from app.core.config import config
from app.core.dependencies.rabbitmq import get_rabbitmq
from app.core.dependencies.redis import get_redis

router = APIRouter(**config.SERVICES["authentication"].to_dict())


@router.post("")
async def authenticate(
    credentials: dict,
    redis=Depends(get_redis),
    rabbitmq: Connection = Depends(get_rabbitmq),
) -> dict:
    """
    Аутентифицирует пользователя.

    Args:
        credentials (dict): Учетные данные пользователя
        redis: Redis клиент для кэширования токенов
        rabbitmq: RabbitMQ соединение для общения с auth_service

    Returns:
        dict: Ответ от auth_service с токеном доступа
    """
    async with rabbitmq.channel() as channel:
        queue = await channel.declare_queue("auth_queue")

        # Отправляем запрос в auth_service
        await channel.default_exchange.publish(
            Message(
                body=json.dumps(
                    {"action": "authenticate", "data": credentials}
                ).encode()
            ),
            routing_key="auth_queue",
        )

        # Получаем и обрабатываем ответ
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    response = json.loads(message.body.decode())
                    # Кэшируем токен если аутентификация успешна
                    if "access_token" in response:
                        await redis.setex(
                            f"token:{response['access_token']}",
                            3600,
                            credentials["email"],
                        )
                    return response


@router.post("/logout")
async def logout(
    token: str, redis=Depends(get_redis), rabbitmq: Connection = Depends(get_rabbitmq)
) -> dict:
    """
    Выход пользователя из системы.

    Args:
        token (str): Токен доступа для выхода
        redis: Redis клиент для удаления токена из кэша
        rabbitmq: RabbitMQ соединение для общения с auth_service

    Returns:
        dict: Ответ от auth_service о результате выхода
    """
    # Удаляем токен из кэша
    await redis.delete(f"token:{token}")

    async with rabbitmq.channel() as channel:
        queue = await channel.declare_queue("auth_queue")

        # Отправляем запрос в auth_service
        await channel.default_exchange.publish(
            Message(body=json.dumps({"action": "logout", "token": token}).encode()),
            routing_key="auth_queue",
        )

        # Получаем и возвращаем ответ
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    return json.loads(message.body.decode())

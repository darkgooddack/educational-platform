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
from app.core.dependencies import get_redis, get_rabbitmq
from app.schemas import AuthenticationSchema, TokenSchema

router = APIRouter(**config.SERVICES["authentication"].to_dict())


@router.post("")
async def authenticate(
    credentials: AuthenticationSchema,
    redis=Depends(get_redis),
    rabbitmq: Connection = Depends(get_rabbitmq),
) -> TokenSchema | None:
    """
    Аутентифицирует пользователя по email и возвращает JWT токен.

    Args:
        credentials: AuthenticationSchema Данные для аутентификации
        redis: Redis клиент для кэширования токенов
        rabbitmq: RabbitMQ соединение для общения с auth_service

    Returns:
        TokenSchema с access_token и token_type
    
    Raises:
        UserNotFoundError: Если пользователь не найден
    """
    async with rabbitmq.channel() as channel:
        queue = await channel.declare_queue("auth_queue")

        # Преобразуем данные в словарь
        credentials_dict = credentials.model_dump()

        # Отправляем запрос в auth_service
        await channel.default_exchange.publish(
            Message(
                body=json.dumps({
                        "action": "authenticate", 
                        "data": credentials_dict
                    }).encode()
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
    token: str, 
    redis=Depends(get_redis), 
    rabbitmq: Connection = Depends(get_rabbitmq)
) -> dict:
    """
    Выход пользователя из системы.

    Args:
        token (str): Токен доступа для выхода
        redis: Redis клиент для удаления токена из кэша
        rabbitmq: RabbitMQ соединение для общения с auth_service

    Returns:
        Словарь с сообщением об успешном выходе {"message": "Выход выполнен успешно!"}
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

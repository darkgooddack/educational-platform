"""
Модуль для обработки аутентификации и авторизации.

Этот модуль содержит эндпоинты для:
- Аутентификации пользователей
- Выхода из системы
"""

from aio_pika import Connection
from fastapi import APIRouter, Depends

from app.core.config import config
from app.core.rabbit.producer import send_auth_message
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

        response = await send_auth_message(
            channel,
            "authenticate",
            credentials.model_dump()
        )

        if "access_token" in response:
            await redis.setex(
                f"token:{response['access_token']}",
                3600,
                credentials.email
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
    async with rabbitmq.channel() as channel:
        return await send_auth_message(channel, "logout", {"token": token})

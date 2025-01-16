"""
Модуль для обработки аутентификации и авторизации.

Этот модуль содержит эндпоинты для:
- Аутентификации пользователей
- Выхода из системы

TODO:
- Типизация всех ответов через Pydantic модели
- Разделение кодов ошибок для разных проблем
- Асинхронная работа с кэшем
- Правильный порядок операций при логауте
- Вынос работы с кэшем в отдельные функции для чистоты кода
"""

from aio_pika import Connection
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import config
from app.core.dependencies import get_rabbitmq, get_redis
from app.core.messaging.auth import AuthMessageProducer, AuthAction
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

        producer = AuthMessageProducer(channel)
        response, error = await producer.send_auth_message(
            AuthAction.AUTHENTICATE,
            data=credentials.model_dump()
        )
        
        if error:
            raise HTTPException(status_code=503, detail=f"Auth service error: {error}")
        
        if "access_token" in response:
            redis.setex(f"token:{response['access_token']}", 3600, credentials.email)
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
        Словарь с сообщением об успешном выходе {"message": "Выход выполнен успешно!"}
    """
    # Удаляем токен из кэша
    redis.delete(f"token:{token}")

    # Отправляем запрос в auth_service
    async with rabbitmq.channel() as channel:
        producer = AuthMessageProducer(channel)
        return await producer.send_auth_message(
            AuthAction.LOGOUT,
            data={"token": token}
        )

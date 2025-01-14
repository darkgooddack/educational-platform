"""
Модуль для регистрации новых пользователей.

Этот модуль содержит эндпоинт для:
- Регистрации новых пользователей через auth_service
"""

import json

from aio_pika import Connection, Message
from fastapi import APIRouter, Depends

from app.core.config import config
from app.core.dependencies import get_redis, get_rabbitmq

from app.schemas import RegistrationSchema, RegistrationResponseSchema

router = APIRouter(**config.SERVICES["registration"].to_dict())


@router.post("/", response_model=RegistrationResponseSchema)
async def register_user(
    user_data: RegistrationSchema,
    redis=Depends(get_redis),
    rabbitmq: Connection = Depends(get_rabbitmq),
) -> RegistrationResponseSchema:
    """
    Регистрирует нового пользователя.

    Args:
        user_data (dict): Данные нового пользователя
        redis: Redis клиент для кэширования данных
        rabbitmq: RabbitMQ соединение для общения с auth_service

    Returns:
        dict: Ответ от auth_service с результатом регистрации
    """
    async with rabbitmq.channel() as channel:
        queue = await channel.declare_queue("auth_queue")

        # Преобразуем данные в словарь
        user_data_dict = user_data.model_dump()
        
        # Отправляем запрос регистрации в auth_service
        await channel.default_exchange.publish(
            Message(
                body=json.dumps({
                    "action": "register", 
                    "data": user_data_dict
                }).encode()
            ),
            routing_key="auth_queue",
        )

        # Получаем и обрабатываем ответ
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    response = json.loads(message.body.decode())
                    # Кэшируем данные пользователя если регистрация успешна
                    if "user_id" in response:
                        await redis.setex(
                            f"user:{response['user_id']}", 3600, json.dumps(user_data)
                        )
                    return response

"""
Модуль для регистрации новых пользователей.

Этот модуль содержит эндпоинт для:
- Регистрации новых пользователей через auth_service
"""

import json

from aio_pika import Connection
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.core.config import config
from app.core.dependencies import get_rabbitmq, get_redis
from app.core.rabbit.producer import send_auth_message
from app.schemas import RegistrationResponseSchema, RegistrationSchema

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
    try:
        async with rabbitmq.channel() as channel:
            response = await send_auth_message(
                channel, action="register", data=user_data.model_dump()
            )
            # Кэшируем данные пользователя если регистрация успешна
            if "user_id" in response:
                redis.setex(
                    f"user:{response['user_id']}",
                    3600,
                    json.dumps(user_data.model_dump()),
                )

            if "error" in response:
                raise HTTPException(
                    status_code=503, detail="Auth service is not responding"
                )

            return response

    except TimeoutError:
        raise HTTPException(status_code=503, detail="Auth service timeout")

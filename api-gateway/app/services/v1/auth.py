"""
Модуль для работы с сервисом авторизации
"""

import logging

from aio_pika import Connection
from fastapi import HTTPException

from app.core.messaging.auth import AuthAction, AuthMessageProducer
from app.schemas import AuthSchema, TokenSchema

logger = logging.getLogger(__name__)


class AuthService:
    async def _send_message(
        self, rabbitmq: Connection, action: AuthAction, data: dict
    ) -> dict:
        """
        Общий метод для отправки сообщений в auth сервис

        Args:
            rabbitmq: RabbitMQ соединение для общения с auth_service
            action: Действие для отправки сообщения
            data: Данные для отправки

        Returns:
            dict: Ответ от auth сервиса
        """
        async with rabbitmq.channel() as channel:
            producer = AuthMessageProducer(channel)
            response, error = await producer.send_auth_message(action, data)

            if error:
                logger.error("❌ Ошибка auth сервиса: %s", error)
                raise HTTPException(
                    status_code=503, detail=f"Auth service error: {error}"
                )

            return response

    async def authenticate(
        self, credentials: AuthSchema, redis, rabbitmq: Connection
    ) -> TokenSchema:
        """
        Аутентификация пользователя

        Args:
            credentials: Данные для аутентификации
            redis: Redis клиент для кэширования токенов
            rabbitmq: RabbitMQ соединение для общения с auth_service

        Returns:
            TokenSchema: Токен для аутентификации
        """
        response = await self._send_message(
            rabbitmq, AuthAction.AUTHENTICATE, credentials.model_dump()
        )

        if "access_token" in response:
            redis.setex(f"token:{response['access_token']}", 3600, credentials.email)
        return response

    async def logout(self, token: str, redis, rabbitmq: Connection) -> dict:
        """
        Выход пользователя

        Args:
            token: Токен для выхода
            redis: Redis клиент для кэширования токенов
            rabbitmq: RabbitMQ соединение для общения с auth_service

        Returns:
            dict: Ответ от auth сервиса
        """
        redis.delete(f"token:{token}")
        return await self._send_message(rabbitmq, AuthAction.LOGOUT, {"token": token})

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
from fastapi import APIRouter, Depends

from app.core.dependencies import get_rabbitmq, get_redis
from app.schemas import AuthSchema, TokenSchema
from app.services.v1.auth import AuthService

auth_service = AuthService()


def setup_routes(router: APIRouter):
    """
    Настройка маршрутов для аутентификации.

    Args:
        router (APIRouter): Роутер FastAPI

    Routes:
        - POST /auth:
            Аутентификация пользователя
        - POST /logout:
            Выход из системы
    """

    @router.post("")
    async def authenticate(
        credentials: AuthSchema,
        redis=Depends(get_redis),
        rabbitmq: Connection = Depends(get_rabbitmq),
    ) -> TokenSchema:
        """
        Аутентифицирует пользователя по email и возвращает JWT токен.

        Args:
            credentials: AuthSchema Данные для аутентификации
            redis: Redis клиент для кэширования токенов
            rabbitmq: RabbitMQ соединение для общения с auth_service

        Returns:
            TokenSchema с access_token и token_type

        Raises:
            UserNotFoundError: Если пользователь не найден
        """
        return await auth_service.authenticate(credentials, redis, rabbitmq)

    @router.post("/logout")
    async def logout(
        token: str,
        redis=Depends(get_redis),
        rabbitmq: Connection = Depends(get_rabbitmq),
    ) -> dict:
        """
        Выход пользователя из системы.

        Args:
            token (str): Токен доступа для выхода
            redis: Redis клиент для удаления токена из кэша
            rabbitmq: RabbitMQ соединение для общения с auth_service

        Returns:
            Словарь с сообщением об успешном выходе
            {"message": "Выход выполнен успешно!"}
        """
        return await auth_service.logout(token, redis, rabbitmq)


__all__ = ["setup_routes"]

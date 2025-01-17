"""
Схемы для кэширования данных в API Gateway.

Модуль содержит Pydantic-схемы для сериализации/десериализации данных,
хранящихся в кэше (Redis). Используется для кэширования токенов и маршрутов.

Основные схемы:
    - TokenCacheSchema: Схема для кэширования JWT токенов
    - RouteCacheSchema: Схема для кэширования информации о маршрутах

Пример использования:
    token = TokenCacheSchema(
        token="jwt.token.here",
        user_id="user123",
        expires_at=datetime.utcnow()
    )
"""

from datetime import datetime

from .base import BaseSchema


class TokenCacheSchema(BaseSchema):
    """
    Схема для кэширования данных токена авторизации.

    Attributes:
        token (str): JWT токен пользователя
        user_id (str): Уникальный идентификатор пользователя
        expires_at (datetime): Время истечения срока действия токена в UTC
    """

    token: str
    user_id: str
    expires_at: datetime


class RouteCacheSchema(BaseSchema):
    """
    Схема для кэширования информации о маршрутах API.

    Attributes:
        path (str): URL путь маршрута (например, "/api/v1/users")
        service (str): Название микросервиса-обработчика
        method (str): HTTP метод (GET, POST, PUT, DELETE и т.д.)
    """

    path: str
    service: str
    method: str

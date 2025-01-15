"""
Зависимость от базы данных, Redis и RabbitMQ

Функции:
- get_db_session(): Возвращает сессию базы данных.
- get_redis(): Возвращает экземпляр Redis.
- get_rabbitmq(): Возвращает экземпляр RabbitMQ.
- get_current_user(): Возвращает текущий аутентифицированный пользователь.

Классы:
- RabbitMQClient: Синглтон для подключения к RabbitMQ.
- RedisClient: Синглтон для подключения к Redis.

Схемы:
- oauth2_schema: Схема OAuth2 для FastAPI.

"""

from .database import get_db_session
from .redis import get_redis, RedisClient
from .rabbitmq import get_rabbitmq, RabbitMQClient
from .authentication import get_current_user, oauth2_schema

__all__ = [
    "get_db_session",
    "get_redis",
    "get_rabbitmq",
    "RabbitMQClient",
    "RedisClient",
    "oauth2_schema",
    "get_current_user",
]
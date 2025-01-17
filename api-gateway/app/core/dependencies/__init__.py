"""
Зависимость от базы данных, Redis и RabbitMQ

Функции:
- get_db_session(): Возвращает сессию базы данных.
- get_redis(): Возвращает экземпляр Redis.
- get_rabbitmq(): Возвращает экземпляр RabbitMQ.

Классы:
- RabbitMQClient: Синглтон для подключения к RabbitMQ.
- RedisClient: Синглтон для подключения к Redis.

"""

from .database import get_db_session
from .rabbitmq import RabbitMQClient, get_rabbitmq
from .redis import RedisClient, get_redis

__all__ = [
    "get_db_session",
    "get_redis",
    "get_rabbitmq",
    "RabbitMQClient",
    "RedisClient",
]

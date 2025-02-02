"""
Зависимость от базы данных, Redis и RabbitMQ

Функции:
- get_db_session(): Возвращает сессию базы данных.
- get_redis(): Возвращает экземпляр Redis.
- get_rabbitmq(): Возвращает экземпляр RabbitMQ.
- get_current_user(): Возвращает текущий аутентифицированный пользователь.

Схемы:
- oauth2_schema: Схема OAuth2 для FastAPI.

"""

from .auth import get_current_user, oauth2_schema
from .database import get_db_session
from .rabbitmq import get_rabbitmq
from .redis import get_redis
from .s3 import get_s3_session

__all__ = [
    "get_db_session",
    "get_redis",
    "get_rabbitmq",
    "oauth2_schema",
    "get_current_user",
    "get_s3_session"
]

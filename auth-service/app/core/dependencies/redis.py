"""
Модуль для работы с Redis.

Функции:
- get_instance(): Возвращает экземпляр Redis.
- close(): Закрывает подключение к Redis.

"""

from app.core.clients import RedisClient


async def get_redis():
    """
    Получает экземпляр Redis.

    Returns:
        Экземпляр Redis.
    """
    redis = await RedisClient.get_instance()
    return redis

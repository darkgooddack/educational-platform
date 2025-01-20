"""
Модуль для работы с Redis.

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

"""
Модуль для подключения к Redis.
"""
from redis import Redis, from_url

from app.core.config import config


class RedisClient:
    """
    Синглтон для подключения к Redis.

    Attributes:
        _instance: Экземпляр Redis.
    """

    _instance: Redis = None

    @classmethod
    async def get_instance(cls) -> Redis:
        """
        Возвращает экземпляр Redis.

        Returns:
            Экземпляр Redis.
        """
        if not cls._instance:
            cls._instance = from_url(
                url=str(config.redis_url), max_connections=config.redis_pool_size
            )
        return cls._instance

    @classmethod
    async def close(cls):
        """
        Закрывает подключение к Redis.

        Returns:
            None
        """
        if cls._instance:
            cls._instance.close()
            cls._instance = None

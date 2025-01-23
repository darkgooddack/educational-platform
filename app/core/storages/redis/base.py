from typing import Optional
from redis import Redis
from app.core.dependencies.redis import RedisClient

class BaseRedisStorage:
    def __init__(self):
        self._redis: Optional[Redis] = None

    async def _get_redis(self) -> Redis:
        if not self._redis:
            self._redis = await RedisClient.get_instance()
        return self._redis

    async def set(self, key: str, value: str, expires: int = None) -> None:
        redis = await self._get_redis()
        redis.set(key, value, ex=expires)

    async def get(self, key: str) -> Optional[str]:
        redis = await self._get_redis()
        return redis.get(key)

    async def delete(self, key: str) -> None:
        redis = await self._get_redis()
        redis.delete(key)

    async def sadd(self, key: str, value: str) -> None:
        redis = await self._get_redis()
        redis.sadd(key, value)

    async def srem(self, key: str, value: str) -> None:
        redis = await self._get_redis()
        redis.srem(key, value)

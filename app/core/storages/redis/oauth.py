from typing import Optional

from app.core.storages.redis.base import BaseRedisStorage


class OAuthRedisStorage(BaseRedisStorage):
    async def save_verifier(self, state: str, verifier: str) -> None:
        """
        Сохранение версификатора для OAuth провайдера в Redis

        Args:
            state: стэйт для OAuth провайдера
            verifier: версификатор для OAuth провайдера
        Returns:
            None
        """
        await self.set(f"oauth:verifier:{state}", verifier, expires=300)

    async def get_verifier(self, state: str) -> Optional[str]:
        """
        Получение verifier по state

        Args:
            state: стэйт для OAuth провайдера
        Returns:
            verifier: версификатор для OAuth провайдера
        """
        return await self.get(f"oauth:verifier:{state}")

    async def delete_verifier(self, state: str) -> None:
        """
        Удаление версификатора

        Args:
            state: стэйт для OAuth провайдера
        Returns:
            None
        """
        await self.delete(f"oauth:verifier:{state}")
from datetime import datetime, timedelta
import json
from typing import Optional

from app.core.storages.redis.base import BaseRedisStorage
from app.core.security import TokenMixin
from app.schemas import UserSchema

class AuthRedisStorage(BaseRedisStorage, TokenMixin):
    """
    Redis хранилище для авторизации.

    """
    async def save_token(self, user: UserSchema, token: str) -> None:
        """
        Сохраняет токен пользователя в Redis.

        Args:
            user: Данные пользователя.
            token: Токен пользователя.

        Returns:
            None
        """
        user_data = self._prepare_user_data(user)

        await self.set(
            key=f"token:{token}",
            value=json.dumps(user_data),
            expires=TokenMixin.get_token_expiration()
        )
        await self.sadd(f"sessions:{user.email}", token)

    async def get_user_by_token(self, token: str) -> Optional[UserSchema]:
        """
        Получает пользователя по токену.

        Args:
            token: Токен пользователя.

        Returns:
            Данные пользователя или None, если пользователь не найден.
        """
        user_data = await self.get(f"token:{token}")
        return UserSchema.model_validate_json(user_data) if user_data else None

    async def remove_token(self, token: str) -> None:
        """
        Удаляет токен пользователя из Redis.

        Args:
            token: Токен пользователя.

        Returns:
            None
        """
        user_data = await self.get(f"token:{token}")
        if user_data:
            user = UserSchema.model_validate_json(user_data)
            await self.srem(f"sessions:{user.email}", token)
        await self.delete(f"token:{token}")

    @staticmethod
    def _prepare_user_data(user: UserSchema) -> dict:
        """
        Подготовка данных пользователя для сохранения

        Конвертируем datetime в строки для отправки в Redis,
        иначе TypeError: Object of type datetime is not JSON serializable

        Args:
            user: Данные пользователя.

        Returns:
            Данные пользователя для сохранения.
        """
        user_data = user.to_dict()
        for key, value in user_data.items():
            if isinstance(value, datetime):
                user_data[key] = value.isoformat()
        return user_data

    async def get_user_from_redis(self, token: str, email: str) -> UserSchema:
        """
        Получает пользователя из Redis или создает базовый объект

        Args:
            token: Токен пользователя.
            email: Email пользователя.

        Returns:
            Данные пользователя.
        """
        stored_token = await self.get(f"token:{token}")

        if stored_token:
            user_data = json.loads(stored_token)
            return UserSchema.model_validate(user_data)

        return UserSchema(email=email)

    async def verify_and_get_user(self, token: str) -> UserSchema:
        """
        Основной метод проверки токена и получения пользователя

        Args:
            token: Токен пользователя.

        Returns:
            Данные пользователя.
        """
        payload = self.verify_token(token)
        email = self.validate_payload(payload)
        return await self.get_user_from_redis(token, email)
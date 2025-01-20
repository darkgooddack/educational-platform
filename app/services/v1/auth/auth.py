"""
Модуль для работы с пользователями.
В данном модуле реализованы функции для работы с пользователями,
включая аутентификацию и авторизацию.
"""

import json
from datetime import datetime

from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clients import RedisClient
from app.core.config import config
from app.core.exceptions import (InvalidCredentialsError, TokenExpiredError,
                                 TokenMissingError)
from app.core.security import HashingMixin, TokenMixin
from app.models import UserModel
from app.schemas import AuthSchema, TokenSchema, UserSchema

from ..base import BaseDataManager, BaseService
from .users import UserDataManager


class AuthService(HashingMixin, TokenMixin, BaseService):
    """
    Сервис для аутентификации пользователей.

    Этот класс предоставляет методы для аутентификации пользователей,
    включая создание нового пользователя,
    аутентификацию пользователя и получение токена доступа.

    Args:
        session: Асинхронная сессия для работы с базой данных.

    Methods:
        authenticate: Аутентифицирует пользователя.
        get_token: Получает токен доступа.
    """

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self._data_manager = AuthDataManager(session)

    async def authenticate(
        self, credentials: AuthSchema
    ) -> TokenSchema:
        """
        Аутентифицирует пользователя по логину и паролю.

        Args:
            auth: Данные для аутентификации пользователя.

        Returns:
            Токен доступа.

        Raises:
            InvalidCredentialsError: Если пользователь не найден или пароль неверный.

        TODO:
            - Добавить логирование ошибок
            - Добавить эксепшены (подумать какие)

        """
        user_model = await UserDataManager(self.session).get_user_by_email(
            credentials.email
        )

        if not user_model or not self.verify(
            user_model.hashed_password, credentials.password
        ):
            raise InvalidCredentialsError()

        user_schema = UserSchema.model_validate(user_model)
        
        return await self.create_token(user_schema)

    async def create_token(user: UserSchema) -> TokenSchema:
        """
        Создание JWT токена

        Args:
            user: Данные пользователя

        Returns:
            TokenSchema: Схема с access_token и token_type
        """
        payload = TokenMixin.create_payload(user)
        token = TokenMixin.generate_token(payload)
        await self._data_manager.save_token(user, token)

        return TokenSchema(
            access_token=token, 
            token_type=config.token_type
        )

    async def logout(self, token: str) -> dict:
        """
        Выполняет выход пользователя, удаляя токен из Redis.
        Отправляем сообщение об успешном завершении.

        Args:
            token: Токен для выхода.

        Returns:
            Сообщение об успешном завершении.
        """
        try:
            await self._data_manager.remove_token(token)
        except RedisError:
            pass
        return {"message": "Выход выполнен успешно!"}


class AuthDataManager(BaseDataManager):
    """
    Класс для работы с данными пользователей в базе данных.

    Args:
        session: Асинхронная сессия для работы с базой данных.
        schema: Схема данных пользователя.
        model: Модель данных пользователя.

    Methods:
        - _prepare_user_data: Подготовка данных пользователя для сохранения.
        - save_token: Сохраняет токен пользователя в Redis.
        - remove_token: Удаляет токен пользователя из Redis.
        - get_user_by_token: Получает данные пользователя по токену.
        - get_user_from_redis: Получает данные пользователя из Redis.
        - verify_token: Проверяет токен пользователя.
        - validate_payload: Проверяет валидность данных пользователя
        - verify_and_get_user: Проверяет токен пользователя и возвращает данные пользователя.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    @staticmethod
    def _prepare_user_data(user: UserSchema) -> dict:
        """
        Подготовка данных пользователя для сохранения

        Args:
            user: Данные пользователя.

        Returns:
            Данные пользователя для сохранения.
        """
        user_data = user.model_dump()

        # Конвертируем datetime в строки для отправки в Redis,
        # иначе TypeError: Object of type datetime is not JSON serializable
        for key, value in user_data.items():
            if isinstance(value, datetime):
                user_data[key] = value.isoformat()
        return user_data

    async def save_token(self, user: UserSchema, token: str) -> None:
        """
        Сохраняет токен пользователя в Redis.

        Args:
            user: Данные пользователя.
            token: Токен пользователя.

        Returns:
            None

        Raises:
            RedisError: Ошибка при работе с Redis.
        """
        user_data = self._prepare_user_data(user)
        # Если JWT создан успешно - сохраняем в Redis
        try:
            redis = await RedisClient.get_instance()
            # Сохраняем токен
            redis.set(
                f"token:{token}",
                json.dumps(user_data),
                ex=TokenMixin.get_token_expiration(),
            )
            # Добавляем в список сессий пользователя
            redis.sadd(f"sessions:{user.email}", token)
        except RedisError:
            # Redis недоступен - возвращаем только JWT
            pass

    async def remove_token(self, token: str) -> None:
        """
        Удаляет токен пользователя из Redis.

        Args:
            token: Токен пользователя.

        Returns:
            None
        """
        redis = await RedisClient.get_instance()
        user_data = redis.get(f"token:{token}")
        if user_data:
            user = UserSchema.model_validate_json(user_data)
            redis.srem(f"sessions:{user.email}", token)
        redis.delete(f"token:{token}")

    async def get_user_by_token(self, token: str) -> UserSchema | None:
        """
        Получает пользователя по токену.

        Args:
            token: Токен пользователя.

        Returns:
            Данные пользователя или None, если пользователь не найден.
        """
        redis = await RedisClient.get_instance()
        user_data = redis.get(f"token:{token}")
        return UserSchema.model_validate_json(user_data) if user_data else None

    async def get_user_from_redis(self, token: str, email: str) -> UserSchema:
        """
        Получает пользователя из Redis или создает базовый объект

        Args:
            token: Токен пользователя.
            email: Email пользователя.

        Returns:
            Данные пользователя.
        """
        try:
            redis = await RedisClient.get_instance()
            stored_token = redis.get(f"token:{token}")

            if stored_token:
                user_data = json.loads(stored_token)
                return UserSchema.model_validate(user_data)
            raise TokenExpiredError()

        except RedisError:
            return UserSchema(email=email)

    async def verify_token(self, token: str) -> dict:
        """
        Проверяет JWT токен и возвращает payload

        Args:
            token: Токен пользователя.

        Returns:
            payload: Данные пользователя.
        """
        if not token:
            raise TokenMissingError()
        return TokenMixin.decode_token(token)

    def validate_payload(self, payload: dict) -> tuple[str, str]:
        """
        Валидирует данные из payload

        Args:
            payload: Данные пользователя.

        Returns:
            email: Email пользователя.
        """
        email = payload.get("sub")
        expires_at = payload.get("expires_at")

        if not email:
            raise InvalidCredentialsError()

        if TokenMixin.is_expired(expires_at):
            raise TokenExpiredError()

        return email

    async def verify_and_get_user(self, token: str) -> UserSchema:
        """
        Основной метод проверки токена и получения пользователя

        Args:
            token: Токен пользователя.

        Returns:
            Данные пользователя.
        """
        payload = await self.verify_token(token)
        email = self.validate_payload(payload)
        return await self.get_user_from_redis(token, email)

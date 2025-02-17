"""
Модуль для работы с пользователями.
В данном модуле реализованы функции для работы с пользователями.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    InvalidCredentialsError, UserInactiveError, 
    TokenExpiredError, TokenInvalidError
)
from app.core.security import HashingMixin, TokenMixin
from app.core.storages.redis.auth import AuthRedisStorage
from app.schemas import (AuthSchema, TokenResponseSchema, TokenSchema,
                         UserCredentialsSchema)
from app.services.v1.base import BaseService

from .data_manager import AuthDataManager

logger = logging.getLogger(__name__)


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
        self._redis_storage = AuthRedisStorage()

    async def authenticate(self, credentials: AuthSchema) -> TokenResponseSchema:
        """
        Аутентифицирует пользователя по логину и паролю.

        Args:
            auth: Данные для аутентификации пользователя.

        Returns:
            TokenResponseSchema: Токен доступа.

        Raises:
            InvalidCredentialsError: Если пользователь не найден или пароль неверный.

        TODO:
            - Добавить логирование ошибок
            - Добавить эксепшены (подумать какие)

        """



        user_model = await self._data_manager.get_user_by_credentials(credentials.email)

        logger.info(
            "Начало аутентификации",
            extra={
                "email": credentials.email,
                "user_found": bool(user_model)
            }
        )

        if not user_model:
            logger.warning(
                "Пользователь не найден",
                extra={"email": credentials.email}
            )
            raise InvalidCredentialsError()

        if not user_model.is_active:
            logger.warning(
                "Попытка входа в неактивный аккаунт",
                extra={"email": credentials.email, "user_id": user_model.id}
            )
            raise UserInactiveError(
                message="Аккаунт деактивирован", extra={"email": credentials.email}
            )

        if not user_model or not self.verify(
            user_model.hashed_password, credentials.password
        ):
            logger.warning(
                "Неверный пароль",
                extra={"email": credentials.email, "user_id": user_model.id}
            )
            raise InvalidCredentialsError()

        user_schema = UserCredentialsSchema.model_validate(user_model)

        logger.info(
            "Аутентификация успешна",
            extra={
                "user_id": user_schema.id,
                "email": user_schema.email,
                **({"role": user_schema.role} if hasattr(user_schema, "role") else {})
            }
        )

        # Обновляем статус при входе
        await self._data_manager.update_online_status(
            user_id=user_model.id, 
            is_online=True
        )

        return await self.create_token(user_schema)

    async def create_token(
        self, user_schema: UserCredentialsSchema
    ) -> TokenResponseSchema:
        """
        Создание JWT токена

        Args:
            user_schema: Данные пользователя

        Returns:
            TokenResponseSchema: Схема с access_token и token_type
        """
        payload = TokenMixin.create_payload(user_schema)
        logger.debug("Создан payload токена", extra={"payload": payload})

        token = TokenMixin.generate_token(payload)
        logger.debug("Сгенерирован токен", extra={"token_length": len(token)})

        await self._redis_storage.save_token(user_schema, token)
        logger.info(
            "Токен сохранен в Redis",
            extra={
                "user_id": user_schema.id,
                "token_length": len(token)
            }
        )

        return TokenResponseSchema(
            access_token=token,
            token_type="bearer",
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
            # Получаем данные из токена
            payload = TokenMixin.decode_token(token)

            # Получаем email пользователя
            user_email = payload.get("sub")

            # Получаем пользователя
            user = await self._data_manager.get_user_by_credentials(user_email)

            if user:
                # Обновляем статус
                await self._data_manager.update_online_status(
                    user_id=user.id, 
                    is_online=False
                )

            # Удаляем токен из Redis
            await self._redis_storage.remove_token(token)

            return {"message": "Выход выполнен успешно!"}
        
        except (TokenExpiredError, TokenInvalidError):
            # Даже если токен невалидный, все равно пытаемся его удалить
            await self._redis_storage.remove_token(token)
            return {"message": "Выход выполнен успешно!"}

    async def check_expired_sessions(self):
        """
        Проверяет истекшие сессии и обновляет статус пользователей
        """
        # Получаем все активные токены из Redis
        active_tokens = await self._redis_storage.get_all_tokens()

        for token in active_tokens:
            try:
                payload = TokenMixin.decode_token(token)
                # Если токен валидный - пропускаем
                continue
            except TokenExpiredError:
                # Токен истек
                user_email = payload.get("sub")
                user = await self._data_manager.get_user_by_credentials(user_email)
                if user:
                    await self._data_manager.update_online_status(user.id, False)
                await self._redis_storage.remove_token(token)

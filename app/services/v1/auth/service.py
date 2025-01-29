"""
Модуль для работы с пользователями.
В данном модуле реализованы функции для работы с пользователями.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidCredentialsError, UserInactiveError
from app.core.security import HashingMixin, TokenMixin
from app.core.storages.redis.auth import AuthRedisStorage
from app.schemas import AuthSchema, TokenSchema, UserCredentialsSchema
from app.services.v1.base import BaseService

from .data_manager import AuthDataManager


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

    async def authenticate(self, credentials: AuthSchema) -> TokenSchema:
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
        user_model = await self._data_manager.get_user_by_credentials(credentials.email)

        if not user_model.is_active:
            raise UserInactiveError(
                message="Аккаунт деактивирован",
                extra={"email": credentials.email}
            )

        if not user_model or not self.verify(
            user_model.hashed_password, credentials.password
        ):
            raise InvalidCredentialsError()

        user_schema = UserCredentialsSchema.model_validate(user_model)

        return await self.create_token(user_schema)

    async def create_token(self, user_schema: UserCredentialsSchema) -> TokenSchema:
        """
        Создание JWT токена

        Args:
            user_schema: Данные пользователя

        Returns:
            TokenSchema: Схема с access_token и token_type
        """
        payload = TokenMixin.create_payload(user_schema)
        token = TokenMixin.generate_token(payload)
        await self._redis_storage.save_token(user_schema, token)

        return TokenSchema(access_token=token, token_type="bearer")

    async def logout(self, token: str) -> dict:
        """
        Выполняет выход пользователя, удаляя токен из Redis.
        Отправляем сообщение об успешном завершении.

        Args:
            token: Токен для выхода.

        Returns:
            Сообщение об успешном завершении.
        """

        await self._redis_storage.remove_token(token)
        return {"message": "Выход выполнен успешно!"}

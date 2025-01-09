"""
Модуль для работы с пользователями.
В данном модуле реализованы функции для работы с пользователями,
включая аутентификацию и авторизацию.
"""

import logging
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from api.schemas.v1.users import UserSchema, CreateUserSchema
from api.services.v1.base import BaseService, BaseDataManager
from api.models.v1.users import UserModel
from api.core.config import env_config
from api.errors.v1.users import (
    UserNotFoundError,
    UserExistsError,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HashingMixin:
    """
    Миксин для хеширования и паролей.

    Этот миксин предоставляет метод для хеширования паролей с использованием bcrypt.

    Methods:
        bcrypt: Хеширует пароль с использованием bcrypt.
    """

    @staticmethod
    def bcrypt(password: str) -> str:
        """
        Генерирует хеш пароля с использованием bcrypt.

        Args:
            password: Пароль для хеширования.

        Returns:
            Хеш пароля.
        """
        return pwd_context.hash(password)



class RegistrationService(HashingMixin, BaseService):
    """
    Сервис для регистрации пользователей.

    Этот класс предоставляет методы для регистрации нового пользователя.

    Args:
        session: Асинхронная сессия для работы с базой данных.

    Methods:
        create_user: Создает нового пользователя и возвращает токен.
    """

    async def create_user(self, user: CreateUserSchema) -> UserSchema:
        """
        Создает нового пользователя в базе данных с использованием данных web формы.

        Args:
            user: Данные нового пользователя.

        Returns:
            Экземпляр созданного пользователя.
        """
        data_manager = RegistrationDataManager(self.session)

        try:
            await data_manager.get_user_by_name(user.name)
            raise UserExistsError("name", user.name)
        except UserNotFoundError:
            pass

        try:
            await data_manager.get_user_by_email(user.email)
            raise UserExistsError("email", user.email)
        except UserNotFoundError:
            pass

        user_model = UserModel(
            name=user.name,
            email=user.email,
            hashed_password=self.bcrypt(user.password)
        )
        return await data_manager.add_user(user_model)


class RegistrationDataManager(BaseDataManager):
    """
    Класс для работы с данными пользователей в базе данных.

    Args:
        session: Асинхронная сессия для работы с базой данных.
        schema: Схема данных пользователя.
        model: Модель данных пользователя.

    Methods:
        add_user: Добавляет нового пользователя в базу данных.
        get_user_by_name: Получает пользователя по name.
        get_user_by_email: Получает пользователя по email.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def add_user(self, user: UserModel) -> None:
        """
        Добавляет нового пользователя в базу данных.

        Args:
            user: Пользователь для добавления.

        Returns:
            None
        """
        try:
            return await self.add_one(user)
        except IntegrityError as e:
            if "users.email" in str(e):
                raise UserExistsError("email", user.email) from e
            elif "users.name" in str(e):
                raise UserExistsError("name", user.name) from e
            raise e

    async def get_user_by_name(self, name: str) -> UserSchema:
        """
        Получает пользователя по имени.

        Args:
            name: Имя пользователя.

        Returns:
            Данные пользователя.
        """
        statement = select(self.model).where(self.model.name == name)
        user = await self.get_one(statement)
        if not user:
            raise UserNotFoundError("name", name)
        return user

    async def get_user_by_email(self, email: str) -> UserSchema:
        """
        Получает пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            Данные пользователя.
        """
        statement = select(self.model).where(self.model.email == email)
        user = await self.get_one(statement)
        if not user:
            raise UserNotFoundError("email", email)
        return user

from typing import Any
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserExistsError

from app.models import UserModel
from app.schemas import UserSchema, UserUpdateSchema
from app.services import BaseEntityManager

class UserDataManager(BaseEntityManager[UserSchema]):
    """
    Менеджер данных для работы с пользователями в БД.

    Реализует низкоуровневые операции для работы с таблицей пользователей.
    Обрабатывает исключения БД и преобразует их в доменные исключения.

    Attributes:
        session (AsyncSession): Асинхронная сессия БД
        schema (Type[UserSchema]): Схема сериализации данных
        model (Type[UserModel]): Модель пользователя

    Methods:
        add_user: Добавление пользователя в БД
        get_user_by_email: Получение пользователя по email
        get_user_by_phone: Получение пользователя по телефону
        update_user: Обновление данных пользователя
        delete_user: Удаление пользователя

    Raises:
        UserNotFoundError: Когда пользователь не найден
        UserExistsError: При попытке создать дубликат пользователя
        IntegrityError: При нарушении целостности данных
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def add_user(self, user: UserModel) -> UserModel:
        """
        Добавляет нового пользователя в базу данных.

        Args:
            user: Пользователь для добавления.

        Returns:
            UserSchema: Данные пользователя.
        """
        try:
            return await self.add_one(user)
        except IntegrityError as e:
            if "users.email" in str(e):
                self.logger.error("add_user: Пользователь с email '%s' уже существует", user.email)
                raise UserExistsError("email", user.email) from e
            elif "users.phone" in str(e):
                self.logger.error("add_user: Пользователь с телефоном '%s' уже существует", user.phone)
                raise UserExistsError("phone", user.phone) from e
            else:
                self.logger.error("Ошибка при добавлении пользователя: %s", e)
                raise


    async def get_user_by_email(self, email: str) -> UserSchema | None:
        """
        Получает пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            UserSchema | None: Данные пользователя или None.

        """
        statement = select(self.model).where(self.model.email == email)
        user = await self.get_one(statement)
        return user

    async def get_user_by_phone(self, phone: str) -> UserSchema | None:
        """
        Получает пользователя по номеру телефона

        Args:
            phone: Номер телефона пользователя.

        Returns:
            UserSchema | None: Данные пользователя или None.
        """
        statement = select(self.model).where(self.model.phone == phone)
        user = await self.get_one(statement)
        return user

    async def get_by_field(self, field: str, value: Any) -> UserSchema | None:
        """
        Получает пользователя по полю.

        Args:
            field: Поле пользователя.
            value: Значение поля пользователя.

        Returns:
            UserSchema | None: Данные пользователя или None.
        """
        statement = select(self.model).where(getattr(self.model, field) == value)
        data = await self.get_one(statement)
        self.logger.debug("data: %s", data)
        return data

    async def update_user(self, user_id: int, data: dict) -> UserUpdateSchema:
        """
        Обновляет данные пользователя.

        Args:
            user_id: Идентификатор пользователя.
            data: Данные для обновления.

        Returns:
            UserUpdateSchema: Обновленные данные пользователя.
        """
        user = await self.get_one(user_id)

        updated_user = UserUpdateSchema(**data)

        return await self.update_one(user, updated_user)

    async def delete_user(self, user_id: int) -> None:
        """
        Удаляет пользователя из базы данных.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            None

        Note:
            #! Можно рассмотреть реализацию мягкого удаления.
        """
        return await self.delete_item(user_id)

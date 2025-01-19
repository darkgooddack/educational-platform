"""
Модуль для работы с пользователями.

Этот модуль содержит основные классы для управления пользователями в системе:
- UserService: Сервисный слой для бизнес-логики работы с пользователями
- UserDataManager: Слой доступа к данным для работы с БД

Основные операции:
- Создание пользователей
- Получение пользователей по email
- Обновление данных пользователей
- Удаление пользователей

Пример использования:
    service = UserService(session)
    user = await service.create_user(user_data)
    user_by_email = await service.get_by_email("test@test.com")
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserExistsError, UserNotFoundError
from app.core.security import HashingMixin
from app.models import UserModel
from app.schemas import (RegistrationResponseSchema, RegistrationSchema,
                         UserSchema, UserUpdateSchema, OAuthUserSchema, UserRole)
from app.services.v1.base import BaseEntityManager, BaseService


class UserService(HashingMixin, BaseService):
    """
    Сервис для управления пользователями.

    Предоставляет высокоуровневые методы для работы с пользователями,
    инкапсулируя бизнес-логику и взаимодействие с базой данных.

    Attributes:
        session (AsyncSession): Асинхронная сессия для работы с БД
        _data_manager (UserDataManager): Менеджер для работы с данными пользователей

    Methods:
        create_user: Создание нового пользователя
        get_by_email: Получение пользователя по email
        get_by_phone: Получение пользователя по телефону
        !# Обновление и удаления пользователя являются лишними в микросервисе auth-service
        update_user: Обновление данных пользователя
        delete_user: Удаление пользователя
    """

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self._data_manager = UserDataManager(session)

    async def create_user(self, user: RegistrationSchema) -> RegistrationResponseSchema:
        """
        Создает нового пользователя в базе данных с использованием данных web формы или OAuth аутентификации.

        Args:
            user: Данные нового пользователя.

        Returns:
            RegistrationResponseSchema: Данные нового пользователя.
            {
                user_id (int): ID пользователя,
                email (str): Email пользователя
                message (str): Сообщение об успешном создании пользователя
            }
        Note:
            - OAuthUserSchema дополнена полями провайдеров
            - Поиск пользователя сначала по provider_id, потом по email
            - create_user поддерживает оба типа схем
            - Валидация телефона только для обычной регистрации
            - Корректная обработка необязательных полей
        """
        self.logger.info(f"Создание пользователя с параметрами: {user.model_dump()}")
        data_manager = UserDataManager(self.session)

        try:
            await data_manager.get_user_by_email(user.email)
            raise UserExistsError("email", user.email)
        except UserNotFoundError:
            pass

        # Проверяем телефон только для обычной регистрации
        if isinstance(user, RegistrationSchema) and user.phone:
            try:
                await data_manager.get_user_by_phone(user.phone)
                raise UserExistsError("phone", user.phone)
            except UserNotFoundError:
                pass

        # Создаем модель пользователя
        user_data = user.model_dump(exclude_unset=True)
        if isinstance(user, OAuthUserSchema):
            user_data["phone"] = None

        user_model = UserModel(
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            email=user.email,
            phone=user.phone,
            hashed_password=self.hash_password(user.password),
            role=UserRole.USER,
            avatar_url=None,
            vk_id=None,
            google_id=None,
            yandex_id=None
        )

        created_user = await data_manager.add_user(user_model)
        return RegistrationResponseSchema(
            user_id=created_user.id,
            email=created_user.email
        )

    async def get_by_field(self, field: str, value: str) -> UserSchema:
        """
        Получает пользователя по заданному полю.

        Args:
            field: Поле для поиска.
            value: Значение поля для поиска.
        Returns:
            UserSchema: Данные пользователя.
        """
        return await self._data_manager.get_by_field(field, value)

    async def get_by_email(self, email: str) -> UserSchema:
        """
        Получает пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            UserSchema: Данные пользователя.
        """
        return await self._data_manager.get_user_by_email(email)

    async def get_by_phone(self, phone: str) -> UserSchema:
        """
        Получает пользователя по phone.

        Args:
            phone: Phone пользователя.

        Returns:
            UserSchema: Данные пользователя.
        """
        return await self._data_manager.get_user_by_phone(phone)

    async def update_user(self, user_id: int, data: dict) -> UserSchema:
        """
        Обновляет данные пользователя.

        Args:
            user_id: Идентификатор пользователя.
            data: Данные для обновления.

        Returns:
            UserSchema: Обновленные данные пользователя.
        """
        return await self._data_manager.update_user(user_id, data)

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
        return await self._data_manager.delete_user(user_id)


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
        !# Обновление и удаления пользователя являются лишними в микросервисе auth-service
        update_user: Обновление данных пользователя
        delete_user: Удаление пользователя

    Raises:
        UserNotFoundError: Когда пользователь не найден
        UserExistsError: При попытке создать дубликат пользователя
        IntegrityError: При нарушении целостности данных
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def add_user(self, user: UserModel) -> UserSchema:
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
            if "users.email" in f"{e}":
                raise UserExistsError("email", user.email) from e
            elif "users.phone" in f"{e}":
                raise UserExistsError("phone", user.phone) from e
            raise e

    async def get_user_by_email(self, email: str) -> UserSchema:
        """
        Получает пользователя по email.
        Args:
            email: Email пользователя.

        Returns:
            UserSchema: Данные пользователя.

        """
        statement = select(self.model).where(self.model.email == email)
        user = await self.get_one(statement)
        if not user:
            raise UserNotFoundError("email", email)
        return user

    async def get_user_by_phone(self, phone: str) -> UserSchema:
        """
        Получает пользователя по номеру телефона
        Args:
            phone: Номер телефона пользователя.

        Returns:
            Данные пользователя.
        """
        statement = select(self.model).where(self.model.phone == phone)
        user = await self.get_one(statement)
        if not user:
            raise UserNotFoundError("phone", phone)
        return user

    async def get_by_field(self, field: str, value: str) -> UserSchema:
        """
        Получает пользователя по полю.

        Args:
            field: Поле пользователя.
            value: Значение поля пользователя.

        Returns:
            Данные пользователя.
        """
        statement = select(self.model).where(getattr(self.model, field) == value)
        user = await self.get_one(statement)
        if not user:
            raise UserNotFoundError(field, value)
        return user

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

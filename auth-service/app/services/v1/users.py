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
from app.schemas import RegistrationSchema, RegistrationResponseSchema, UserSchema
from app.services import BaseEntityManager, BaseService


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
        super().__init__(session)
        self._data_manager = UserDataManager(self.session)

    async def create_user(self, user: RegistrationSchema) -> RegistrationResponseSchema:
        """
        Создает нового пользователя в базе данных с использованием данных web формы.

        Args:
            user: Данные нового пользователя.

        Returns:
            RegistrationResponseSchema: Данные нового пользователя.
        """
        data_manager = UserDataManager(self.session)

        try:
            await data_manager.get_user_by_email(user.email)
            raise UserExistsError("email", user.email)
        except UserNotFoundError:
            pass

        try:
            await data_manager.get_user_by_phone(user.phone)
            raise UserExistsError("phone", user.phone)
        except UserNotFoundError:
            pass

        user_model = UserModel(
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            email=user.email,
            phone=user.phone,
            hashed_password=self.bcrypt(user.password),
        )
        return await data_manager.add_user(user_model)

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
            if "users.email" in str(e):
                raise UserExistsError("email", user.email) from e
            elif "users.phone" in str(e):
                raise UserExistsError("phone", user.phone) from e
            raise e

    async def get_user_by_email(self, email: str) -> UserSchema:
        """
        Получает пользователя по email.
        #! TODO: Перейти на get_by_field
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

    async def get_user_by_phone(self, phone: str) -> UserSchema:
        """
        Получает пользователя по номеру телефона
        #! TODO: Перейти на get_by_field
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

    async def update_user(self, user_id: int, data: dict) -> UserSchema:
        """
        Обновляет данные пользователя.

        Args:
            user_id: Идентификатор пользователя.
            data: Данные для обновления.

        Returns:
            UserSchema: Обновленные данные пользователя.
        """
        user = await self.get_one(user_id)
        for key, value in data.items():
            setattr(user, key, value)
        return await self.update_one(user)

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

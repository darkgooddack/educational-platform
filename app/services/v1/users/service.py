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
    user_by_email = await service.get_user_by_email("test@test.com")
"""

from typing import Any, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserCreationError, UserExistsError
from app.core.security import HashingMixin
from app.models import UserModel
from app.schemas import (ManagerSelectSchema, Page, PaginationParams,
                         RegistrationResponseSchema, RegistrationSchema,
                         UserCredentialsSchema, UserRole, UserSchema,
                         UserUpdateSchema, OAuthUserSchema)
from app.services import BaseService

from .data_manager import UserDataManager


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
        create_oauth_user: Создание пользователя через OAuth
        _create_user_internal: Внутренний метод создания пользователя (для объединения create_user и create_oauth_user)
        get_user_by_field: Получение пользователя по заданному полю
        get_user_by_email: Получение пользователя по email
        get_user_by_phone: Получение пользователя по телефону
        update_user: Обновление данных пользователя
        delete_user: Удаление пользователя
        exists_user: Проверка наличия пользователя по id
        exists_manager: Проверка наличия пользователя с ролью менеджера
    """

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self._data_manager = UserDataManager(session)

    async def assign_role(self, user_id: int, role: UserRole) -> UserUpdateSchema:
        """
        Назначает роль пользователю.

        Args:
            user_id (int): Идентификатор пользователя
            role (UserRole): Роль пользователя

        Returns:
            UserUpdateSchema: Обновленный пользователь
        """
        return await self._data_manager.assign_role(user_id, role)

    async def get_managers(self) -> List[ManagerSelectSchema]:
        """
        Получает список менеджеров.

        Returns:
            List[UserUpdateSchema]: Список менеджеров
        """
        return await self.get_users_by_field("role", UserRole.MANAGER.value)

    async def create_user(self, user: RegistrationSchema) -> RegistrationResponseSchema:
        """
        Создает нового пользователя через веб-форму регистрации.

        Args:
            user: Данные пользователя из формы регистрации

        Returns:
            RegistrationResponseSchema: Схема ответа с id, email и сообщением об успехе
        """

        created_user = await self._create_user_internal(user)

        return RegistrationResponseSchema(
            user_id=created_user.id,
            email=created_user.email,
            message="Регистрация успешно завершена",
        )

    async def create_oauth_user(self, user: OAuthUserSchema) -> UserCredentialsSchema:
        """
        Создает нового пользователя через OAuth аутентификацию.

        Args:
            user: Данные пользователя от OAuth провайдера

        Returns:
            UserCredentialsSchema: Учетные данные пользователя
        """
        created_user = await self._create_user_internal(user)

        self.logger.debug("Созданный пользователь (created_user): %s", vars(created_user))

        return created_user

    async def _create_user_internal(self, user: OAuthUserSchema | RegistrationSchema) -> UserCredentialsSchema:
        """
        Внутренний метод создания пользователя в базе данных.

        Args:
            user: Данные нового пользователя

        Returns:
            UserModel: Созданный пользователь

        Raises:
            UserExistsError: Если пользователь с таким email или телефоном уже существует
            UserCreationError: При ошибке создания пользователя

        Note:
            - Поддерживает данные как из веб-формы, так и от OAuth провайдеров
            - Проверяет уникальность email и телефона
            - Сохраняет идентификаторы OAuth провайдеров
        """
        # Преобразуем в OAuthUserSchema если есть OAuth идентификаторы
        user_dict = user.model_dump()
        if any(key in user_dict for key in ['vk_id', 'google_id', 'yandex_id', 'avatar']):
            user = OAuthUserSchema(**user_dict)
        self.logger.debug(
                    "user теперь имеет тип '%s'", type(user)
                )
        data_manager = UserDataManager(self.session)

        # Проверка email
        existing_user = await data_manager.get_user_by_email(user.email)
        if existing_user:
            self.logger.error("Пользователь с email '%s' уже существует", user.email)
            raise UserExistsError("email", user.email)

        # Проверяем телефон только для обычной регистрации
        if isinstance(user, RegistrationSchema) and user.phone:
            existing_user = await data_manager.get_user_by_phone(user.phone)
            if existing_user:
                self.logger.error(
                    "Пользователь с телефоном '%s' уже существует", user.phone
                )
                raise UserExistsError("phone", user.phone)

        # Создаем модель пользователя
        user_data = user.to_dict()

        vk_id = user_data.get("vk_id")
        google_id = user_data.get("google_id")
        yandex_id = user_data.get("yandex_id")
        self.logger.debug(
                    "user имеет тип '%s'", type(user)
                )
        # Устанавливаем идентификаторы провайдеров, если они есть
        user_model = UserModel(
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            email=user.email,
            phone=user.phone,
            hashed_password=self.hash_password(user.password),
            role=UserRole.USER,
            avatar=user.avatar,
            vk_id=int(vk_id) if vk_id is not None else None,
            google_id=str(google_id) if google_id is not None else None,
            yandex_id=int(yandex_id) if yandex_id is not None else None,
        )

        try:
            created_user = await data_manager.add_user(user_model)

            user_credentials = UserCredentialsSchema(
                id=created_user.id,
                email=created_user.email,
                name=created_user.first_name,
                hashed_password=user_model.hashed_password, #! Костыль
            )
            return user_credentials

        except Exception as e:
            self.logger.error("Ошибка при создании пользователя: %s", e)
            raise UserCreationError(
                "Не удалось создать пользователя. Пожалуйста, попробуйте позже."
            ) from e

    async def exists_user(self, user_id: int) -> bool:
        """
        Проверяет существует ли пользователь с указанным id.

        Args:
            user_id: Идентификатор пользователя

        Returns:
            bool: True, если пользователь существует, False - иначе
        """
        return await self._data_manager.exists_user(user_id)

    async def exists_manager(self, manager_id: int) -> bool:
        """
        Проверяет существует ли менеджер с указанным id.

        Args:
            user_id: Идентификатор менеджера

        Returns:
            bool: True, если менеджер существует, False - иначе
        """
        return await self._data_manager.exists_user_with_role(
            manager_id, UserRole.MANAGER.value
        )

    async def get_user_by_field(
        self, field: str, value: Any
    ) -> UserCredentialsSchema | None:
        """
        Получает пользователя по заданному полю.

        Args:
            field: Поле для поиска.
            value: Значение поля для поиска.
        Returns:
            UserCredentialsSchema | None: Данные пользователя или None.
        """
        return await self._data_manager.get_user_by_field(field, value)

    async def get_user_by_email(self, email: str) -> UserCredentialsSchema | None:
        """
        Получает пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            UserCredentialsSchema | None: Данные пользователя или None.
        """
        return await self._data_manager.get_user_by_email(email)

    async def get_user_by_phone(self, phone: str) -> UserCredentialsSchema | None:
        """
        Получает пользователя по phone.

        Args:
            phone: Phone пользователя.

        Returns:
            UserCredentialsSchema | None: Данные пользователя или None.
        """
        return await self._data_manager.get_user_by_phone(phone)

    async def get_users_by_field(self, field: str, value: Any) -> List[UserSchema]:
        """
        Получает пользователей по заданному полю.

        Args:
            field: Поле для поиска.
            value: Значение поля для поиска.

        Returns:
            List[UserSchema]: Данные пользователя или [].
        """
        return await self._data_manager.get_users_by_field(field, value)

    async def get_users(
        self,
        pagination: PaginationParams,
        role: UserRole = None,
        search: str = None,
    ) -> tuple[List[UserSchema], int]:
        """
        Получает список пользователей с возможностью пагинации, поиска и фильтрации.

        Args:
            pagination (PaginationParams): Параметры пагинации
            role (UserRole): Фильтрация по роли пользователя
            search (str): Поиск по тексту пользователя

        Returns:
            tuple[List[FeedbackSchema], int]: Список пользователей и общее количество пользователей.
        """
        return await self._data_manager.get_users(
            pagination=pagination,
            role=role,
            search=search,
        )

    async def update_user(self, user_id: int, data: dict) -> UserCredentialsSchema:
        """
        Обновляет данные пользователя.

        Args:
            user_id: Идентификатор пользователя.
            data: Данные для обновления.

        Returns:
            UserCredentialsSchema: Обновленные данные пользователя.
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

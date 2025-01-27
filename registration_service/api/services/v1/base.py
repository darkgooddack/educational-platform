from typing import TypeVar, Generic, Type, Any, List
import logging
from sqlalchemy import select, delete
from sqlalchemy.sql.expression import Executable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from api.models.v1.base import BaseModel
from api.schemas.v1.base import BaseSchema

M = TypeVar("M", bound=BaseModel)
T = TypeVar("T", bound=BaseSchema)


class SessionMixin:
    """
    Миксин для предоставления экземпляра сессии базы данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализирует SessionMixin.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
        """
        self.session = session


class BaseService(SessionMixin):
    """
    Базовый класс для сервисов приложения.
    """


class BaseDataManager(SessionMixin, Generic[T]):
    """
    Базовый класс для менеджеров данных с поддержкой обобщенных типов.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных.
        schema (Type[T]): Тип схемы данных.
        model (Type[M]): Тип модели.
    """

    def __init__(self, session: AsyncSession, schema: Type[T], model: Type[M]):
        """
        Инициализирует BaseDataManager.

        Args:
            session (AsyncSession): Асинхронная сессия базы данных.
            schema (Type[T]): Тип схемы данных.
            model (Type[M]): Тип модели.
        """
        super().__init__(session)
        self.schema = schema
        self.model = model

    async def add_one(self, model: Any) -> T:
        """
        Добавляет одну запись в базу данных.

        Args:
            model (Any): Модель для добавления.

        Returns:
            T: Добавленная запись в виде схемы.

        Raises:
            SQLAlchemyError: Если произошла ошибка при добавлении.
        """
        try:
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return self.schema(**model.to_dict())
        except SQLAlchemyError as e:
            await self.session.rollback()
            logging.error("Ошибка при добавлении: %s", e)
            raise

    async def get_one(self, select_statement: Executable) -> Any | None:
        """
        Получает одну запись из базы данных.

        Args:
            select_statement (Executable): SQL-запрос для выборки.

        Returns:
            Any | None: Полученная запись или None, если запись не найдена.

        Raises:
            SQLAlchemyError: Если произошла ошибка при получении записи.
        """
        try:
            result = await self.session.execute(select_statement)
            return result.scalar()
        except SQLAlchemyError as e:
            logging.error("Ошибка при получении записи: %s", e)
            return None



class BaseEntityManager(BaseDataManager[T]):
    """Базовый менеджер для работы с сущностями.

    Предоставляет базовые CRUD операции для всех типов сущностей.

    Args:
        session: Сессия базы данных SQLAlchemy
        schema: Класс Pydantic схемы для валидации
        model: Класс SQLAlchemy модели
    """

    def __init__(self, session, schema: Type[T], model: Type[M]):
        """
        Инициализирует менеджер.

        Args:
            session: Сессия базы данных SQLAlchemy
            schema: Класс Pydantic схемы для валидации данных
            model: Класс SQLAlchemy модели
        """
        super().__init__(session, schema, model)
        self.model = model

    async def add_item(self, new_item) -> T:
        """
        Добавляет новый элемент в базу данных.

        Args:
            new_item: Объект для добавления в БД

        Returns:
            T: Добавленный объект в виде схемы
        """
        return await self.add_one(new_item)

    async def get_item(self, item_id: int) -> T | None:
        """
        Получает элемент по ID.

        Args:
            item_id: ID элемента для получения

        Returns:
            T | None: Найденный объект или None
        """
        statement = select(self.model).where(self.model.id == item_id)
        schema: T = await self.get_one(statement)
        return schema

    async def get_items(self, statement=None) -> List[T]:
        """
        Получает список элементов.

        Args:
            statement: SQL выражение для выборки (опционально)

        Returns:
            List[T]: Список объектов в виде схем
        """
        if statement is None:
            statement = select(self.model)
        schemas: List[T] = []
        models = await self.get_all(statement)
        for model in models:
            schemas.append(model)
        return schemas

    async def get_by_name(self, name: str) -> Any | None:
        """
        Получает элемент по имени.

        Args:
            name: Имя для поиска

        Returns:
            Any | None: Найденный объект или None
        """
        statement = select(self.model).where(self.model.name == name)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Any | None:
        """
        Получает элемент по email.

        Args:
            email: Email для поиска

        Returns:
            Any | None: Найденный объект или None
        """
        statement = select(self.model).where(self.model.email == email)
        result = await self.session.execute(statement)
        return result.unique().scalar_one_or_none()

    async def search_items(self, q: str) -> List[T]:
        """
        Поиск элементов по подстроке.

        Args:
            q: Строка для поиска

        Returns:
            List[T]: Список найденных объектов

        Raises:
            AttributeError: Если модель не имеет атрибутов title/name
        """
        if hasattr(M, "title"):
            statement = select(self.model).where(self.model.title.ilike(f"%{q}%"))
        elif hasattr(M, "name"):
            statement = select(self.model).where(self.model.name.ilike(f"%{q}%"))
        else:
            raise AttributeError("Модель не имеет атрибута 'title' или 'name'.")
        return await self.get_items(statement)

    async def update_item(self, item_id: int, updated_item: T) -> T | None:
        """
        Обновляет элемент по ID.

        Args:
            item_id: ID элемента для обновления
            updated_item: Новые данные элемента

        Returns:
            T | None: Обновленный объект или None
        """
        old_item = await self.get_item(item_id)
        schema: T = await self.update_one(old_item, updated_item)
        return schema

    async def delete_item(self, item_id: int) -> bool:
        """
        Удаляет элемент по ID.

        Args:
            item_id: ID элемента для удаления

        Returns:
            bool: True если успешно удален
        """
        statement = delete(self.model).where(self.model.id == item_id)
        return await self.delete(statement)

    async def delete_items(self) -> bool:
        """
        Удаляет все элементы.

        Returns:
            bool: True если успешно удалены
        """
        statement = delete(self.model)
        return await self.delete(statement)

"""
Базовый сервисный слой для работы с БД через SQLAlchemy.

Предоставляет базовые CRUD операции для работы с моделями данных.
Использует generic типы для обеспечения типобезопасности при работе с разными моделями.

Основные возможности:
    - Создание записей
    - Получение записей по фильтрам
    - Удаление записей по фильтрам
    - Автоматическая обработка ошибок БД
    - Автоматический роллбэк при ошибках
"""
from typing import TypeVar, Generic, Type
import logging
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.models import BaseModel
from app.schemas import BaseSchema

M = TypeVar("M", bound=BaseModel)
T = TypeVar("T", bound=BaseSchema)

class BaseService(Generic[T, M]):
    """
    Базовый класс сервиса для CRUD операций.

    Attributes:
        session (AsyncSession): Асинхронная сессия SQLAlchemy
        schema (Type[T]): Класс Pydantic схемы для сериализации
        model (Type[M]): Класс модели SQLAlchemy

    Generic Types:
        T: Тип схемы, наследник BaseSchema
        M: Тип модели, наследник BaseModel
    """
    def __init__(self, session: AsyncSession, schema: Type[T], model: Type[M]):
        self.session = session
        self.schema = schema
        self.model = model

    async def create(self, data: dict) -> T:
        """
        Создает новую запись в БД.

        Args:
            data (dict): Данные для создания записи

        Returns:
            T: Сериализованный объект созданной записи

        Raises:
            SQLAlchemyError: При ошибке работы с БД
        """
        try:
            db_item = self.model(**data)
            self.session.add(db_item)
            await self.session.commit()
            await self.session.refresh(db_item)
            return self.schema.model_validate(db_item)
        except SQLAlchemyError as e:
            await self.session.rollback()
            logging.error("Ошибка при создании записи в базе данных: %s", e)
            raise

    async def get(self, **filters) -> T | None:
        """
        Получает запись из БД по фильтрам.

        Args:
            **filters: Именованные параметры для фильтрации

        Returns:
            T | None: Сериализованный объект или None если не найден
        """
        try:
            query = select(self.model)
            for key, value in filters.items():
                query = query.where(getattr(self.model, key) == value)
            result = await self.session.execute(query)
            item = result.scalar_one_or_none()
            return self.schema.model_validate(item) if item else None
        except SQLAlchemyError as e:
            logging.error("Ошибка при получении записи из базы данных: %s", e)
            return None

    async def delete(self, **filters) -> bool:
        """
        Удаляет запись из БД по фильтрам.

        Args:
            **filters: Именованные параметры для фильтрации

        Returns:
            bool: True если запись удалена, False если возникла ошибка
        """
        try:
            query = delete(self.model)
            for key, value in filters.items():
                query = query.where(getattr(self.model, key) == value)
            result = await self.session.execute(query)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            logging.error("Ошибка при удалении записи из базы данных: %s", e)
            return False

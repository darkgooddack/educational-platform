"""
Модуль base.py содержит базовые классы и типы данных для работы с моделями SQLAlchemy.

Этот модуль предоставляет:
   BaseModel - базовый класс для определения моделей SQLAlchemy с дополнительными методами.

Модуль обеспечивает удобную работу с моделями данных и их преобразование в различные форматы.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Type, TypeVar

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

T = TypeVar("T", bound="BaseModel")


class BaseModel(DeclarativeBase):
    """
    Базовый класс, используемый для определения моделей.

    Предоставляет общие поля и методы для работы с моделями.

    Args:
        id (Mapped[int]): Первичный ключ модели.
        created_at (Mapped[datetime]): Дата и время создания модели.
        updated_at (Mapped[datetime]): Дата и время последнего обновления модели.

        metadata (MetaData): Метаданные для работы с базой данных.

    Methods:
        table_name(): Возвращает имя таблицы, на которую ссылается модель.
        fields(): Возвращает список полей модели.
        to_dict(): Преобразует модель в словарь.
        __repr__(): Возвращает строковое представление модели.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    metadata = MetaData()

    @classmethod
    def table_name(cls) -> str:
        """
        Возвращает имя таблицы, на которую ссылается модель.

        Returns:
            str: Имя таблицы.
        """

        return cls.__tablename__

    @classmethod
    def fields(cls: Type[T]) -> List[str]:
        """
        Возвращает список имен полей модели.

        Returns:
            List[str]: Список имен полей.
        """

        return cls.__mapper__.selectable.c.keys()

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует экземпляр модели в словарь.

        Returns:
            Dict[str, Any]: Словарь, представляющий модель.
        """

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        """
        Строковое представление экземпляра модели для удобства отладки.
        Содержит идентификатор, дату создания и дату последнего обновления.

        Returns:
            str: Строковое представление экземпляра модели.
        """
        return f"<{self.__class__.__name__}(id={self.id})>"

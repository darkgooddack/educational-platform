"""
Модуль для определения базовой схемы данных.

Этот модуль содержит класс `BaseSchema`, который наследуется от
`BaseModel` библиотеки Pydantic. Класс предназначен для использования
в других схемах и предоставляет общую конфигурацию для валидации
и сериализации данных.

Класс `BaseSchema` включает в себя настройки, которые позволяют
использовать атрибуты модели в качестве полей схемы.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Базовая схема для всех моделей данных.

    Этот класс наследуется от `BaseModel` и предоставляет общую
    конфигурацию для всех схем, включая возможность использования
    атрибутов модели в качестве полей схемы.

    Args:
        model_config (ConfigDict): Конфигурация модели, позволяющая
        использовать атрибуты в качестве полей.
        created_at (datetime): Дата и время создания записи.
        updated_at (datetime): Дата и время последнего обновления записи.
    """

    model_config = ConfigDict(from_attributes=True)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return self.model_dump()

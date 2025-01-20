"""
Модуль для определения базовой схемы данных.

Этот модуль содержит класс `CommonBaseSchema`, который наследуется от
`BaseModel` библиотеки Pydantic. Класс предназначен для использования
в других схемах и предоставляет общую конфигурацию для валидации
и сериализации данных.

Класс `BaseSchema` включает в себя настройки, которые позволяют
использовать атрибуты модели в качестве полей схемы.

Класс `BaseInputSchema` - если в использоовании общих атрибутов
из BaseSchema нет необходимости или они будут другие
"""
from typing import TypeVar
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class CommonBaseSchema(BaseModel):
    """
    Общая базовая схема для всех моделей.
    Содержит только общую конфигурацию и метод to_dict().

    Attributes:
        model_config (ConfigDict): Конфигурация модели, позволяющая
        использовать атрибуты в качестве полей.

    Methods:
        to_dict(): Преобразует объект в словарь.
    """

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self) -> dict:
        return self.model_dump()


class BaseSchema(CommonBaseSchema):
    """
    Базовая схема для всех моделей данных.

    Этот класс наследуется от `CommonBaseSchema` и предоставляет общую
    конфигурацию для всех схем, включая возможность использования
    атрибутов модели в качестве полей схемы.

    Attributes:
        id (int): Идентификатор записи.
        created_at (datetime): Дата и время создания записи.
        updated_at (datetime): Дата и время последнего обновления записи.
    """

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BaseInputSchema(CommonBaseSchema):
    """
    Базовая схема для входных данных.
    Этот класс наследуется от `CommonBaseSchema`
    и предоставляет общую конфигурацию для всех схем входных данных.
    """

    pass

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
from typing import TypeVar, Optional, Generic, List
from datetime import datetime

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

T = TypeVar("T", bound=BaseSchema)

class Page(BaseModel, Generic[T]):
    """
    Схема для представления страницы результатов запроса.

    Attributes:
        items (List[T]): Список элементов на странице.
        total (int): Общее количество элементов.
        page (int): Номер текущей страницы.
        size (int): Размер страницы.
    """
    items: List[T]
    total: int
    page: int
    size: int


class PaginationParams:
    """
    Параметры для пагинации.

    Attributes:
        skip (int): Количество пропускаемых элементов.
        limit (int): Максимальное количество элементов на странице.
        sort_by (str): Поле для сортировки.
        sort_desc (bool): Флаг сортировки по убыванию.
    """
    def __init__(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ):
        self.skip = skip
        self.limit = limit
        self.sort_by = sort_by
        self.sort_desc = sort_desc

    @property
    def page(self) -> int:
        """
        Получает номер текущей страницы.

        Returns:
            int: Номер текущей страницы.

        """
        return self.skip // self.limit + 1
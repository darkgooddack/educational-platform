from typing import List, Optional

from ..base import BaseInputSchema, BaseSchema, ListResponseSchema


class ThemeBase(BaseSchema):
    """
    Базовая схема темы с общими полями

    Attributes:
        name (str): Название темы
        description (str): Описание темы
        parent_id (Optional[int]): Идентификатор родительской темы
        children (Optional[List['ThemeBase']]): Список дочерних тем
    """

    name: str
    description: str
    parent_id: Optional[int] = None
    children: Optional[List["ThemeBase"]] = []


class ThemeCreateSchema(BaseInputSchema):
    """
    Схема для создания темы

    Attributes:
        name (str): Название темы
        description (str): Описание темы
        parent_id (Optional[int]): Идентификатор родительской темы
    """

    name: str
    description: str
    parent_id: Optional[int] = None


class ThemeSchema(ThemeBase):
    """Полная схема темы"""

    pass


class ThemeListResponse(ListResponseSchema[ThemeSchema]):
    """
    Схема для списка тем

    Attributes:
        items (List[ThemeSchema]): Список тем
    """

    items: List[ThemeSchema]
    success: bool = True
    message: str = "Тема успешно добавлена"

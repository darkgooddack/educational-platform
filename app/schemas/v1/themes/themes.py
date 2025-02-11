from typing import List, Optional
from app.schemas.v1.pagination import Page
from ..base import BaseInputSchema, BaseSchema, BaseResponseSchema, ListResponseSchema


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

class ThemeCreateResponse(BaseResponseSchema):
    """
    Схема для создания темы
    
    Attributes:
        item (ThemeSchema): Созданная тема
        success (bool): Признак успешного создания
        message (str): Сообщение о создании
    """

    item: ThemeSchema
    success: bool = True
    message: str = "Тема успешно создана"

class ThemeUpdateResponse(BaseResponseSchema):
    """
    Схема для обновления темы

    Attributes:
        id (int): ID обновленной темы
        success (bool): Признак успешного обновления
        message (str): Сообщение об обновлении
    """
    id: int
    success: bool = True
    message: str = "Тема успешно обновлена"

class ThemeDeleteResponse(BaseResponseSchema):
    """
    Схема для удаления тем
    
    Attributes:
        id (int): ID удаленной темы
        success (bool): Признак успешного удаления
        message (str): Сообщение об удалении
    """
    id: int
    success: bool = True
    message: str = "Тема успешно удалена"

class ThemeListResponse(Page[ThemeSchema]):
    """
    Схема для получения списка тем

    Наследуется от Page[ThemeSchema] и добавляет поля success и message
    """
    success: bool = True
    message: str = "Список тем успешно получен"

class ThemeSelectResponse(BaseResponseSchema):
    """
    Схема для простого списка тем (для селектов)

    Attributes:
        items: Список тем без вложенности
        success: Признак успешного получения списка
        message: Сообщение об успешном получении списка
    """
    items: List[ThemeSchema]
    success: bool = True
    message: str = "Список тем получен"

class ThemeTreeResponse(BaseResponseSchema):
    """
    Схема для древовидного списка тем

    Attributes:
        items: Список тем в виде дерева
        success: Признак успешного получения дерева
        message: Сообщение об успешном получении дерева
    """
    items: List[ThemeSchema]
    success: bool = True
    message: str = "Дерево тем успешно получено"

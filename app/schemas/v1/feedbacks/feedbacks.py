"""
Модуль схем обратной связи
"""

from enum import Enum
from typing import Optional, List

from pydantic import EmailStr, Field

from app.schemas.v1.base import BaseInputSchema, BaseSchema, BaseResponseSchema


class FeedbackStatus(str, Enum):
    """
    Статусы обратной связи для обработки администратором

    Attributes:
        PENDING (str): Обратная связь ожидает обработки
        PROCESSED (str): Обратная связь обработана
        DELETED (str): Обратная связь удалена
    """

    PENDING = "pending"
    PROCESSED = "processed"
    DELETED = "deleted"


class FeedbackSchema(BaseSchema):
    """
    Схема обратной связи

    Является маппированным объектом для работы с базой данных

    Attributes:
        manager_id (int | None): ID менеджера, который обрабатывает обратную связь
        name (str): Имя пользователя
        phone (str | None): Телефон пользователя
        email (EmailStr): Электронная почта пользователя
        status (FeedbackStatus): Статус обратной связи

    Наследует:
        id: Optional[int] = None
        created_at: Optional[datetime] = None
        updated_at: Optional[datetime] = None
    """

    manager_id: Optional[int] = None
    name: str = Field(min_length=0, max_length=50, description="Имя пользователя")
    phone: Optional[str] = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )
    email: EmailStr = Field(description="Email пользователя")
    status: FeedbackStatus


class FeedbackCreateSchema(BaseInputSchema):
    """
    Схема создания обратной связи

    Attributes:
        manager_id (int | None): Идентификатор менеджера, которому адресована обратная связь
        name (str): Имя пользователя
        phone (str | None): Телефон пользователя
        email (EmailStr): Электронная почта пользователя
    """

    manager_id: Optional[int] = None
    name: str = Field(min_length=0, max_length=50, description="Имя пользователя")
    phone: Optional[str] = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )
    email: EmailStr = Field(description="Email пользователя")


class FeedbackUpdateSchema(BaseInputSchema):
    """
    Схема обновления обратной связи

    Attributes:
        manager_id (int | None): Идентификатор менеджера, которому адресована обратная связь
        name (str): Имя пользователя
        phone (str | None): Телефон
        email (EmailStr): Электронная почта
        status (FeedbackStatus): Статус обратной связи
    """

    manager_id: Optional[int] = None
    name: str = Field(min_length=0, max_length=50, description="Имя пользователя")
    phone: Optional[str] = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )
    email: EmailStr = Field(description="Email пользователя")
    status: FeedbackStatus


class FeedbackResponse(BaseInputSchema):
    """
    Схема ответа на создание обратной связи.

    Attributes:
        id (int | None): Идентификатор обратной связи.
        manager_id (int | None): ID менеджера, которому адресована обратная связь.
        message (str): Сообщение об успешном создании обратной связи.
    """

    id: Optional[int] = None
    manager_id: Optional[int] = None
    message: str = Field(
        default="Обратная связь успешно отправлена!",
        description="Сообщение, отправляемое после совершенной работы с обратной связью \
            (создание, обновление, удаление)",
        examples=[
            "Обратная связь успешно отправлена!",
            "Обратная связь успешно удалена!",
        ],
    )

class FeedbackCreateResponse(BaseResponseSchema):
    """
    Схема ответа при создании обратной связи

    Attributes:
        item: FeedbackSchema
        success: Признак успешного создания
        message: Сообщение о создании
    """
    item: FeedbackSchema
    success: bool = True
    message: str = "Обратная связь успешно создана"

class FeedbackUpdateResponse(BaseResponseSchema):
    """
    Схема ответа при обновлении обратной связи

    Attributes:
        id: ID обратной связи
        success: Признак успешного обновления
        message: Сообщение об обновлении
    """
    id: int
    success: bool = True
    message: str = "Обратная связь успешно обновлена"

class FeedbackDeleteResponse(BaseResponseSchema):
    """
    Схема ответа при удалении обратной связи

    Attributes:
        id: ID обратной связи
        success: Признак успешного удаления
        message: Сообщение об удалении
    """
    id: int
    success: bool = True
    message: str = "Обратная связь успешно удалена"

class FeedbackListResponse(BaseResponseSchema):
    """
    Схема для возврата списка обратной связи с пагинацией

    Attributes:
        items: Список обратной связи
        total: Общее количество
        page: Текущая страница
        size: Размер страницы
        success: Признак успешного получения
        message: Сообщение об успешном получении
    """
    items: List[FeedbackSchema]
    total: int
    page: int
    size: int
    success: bool = True
    message: str = "Список обратной связи успешно получен"
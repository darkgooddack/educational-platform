"""
Модуль схем обратной связи
"""
from enum import Enum
from pydantic import EmailStr, Field
from ..base import BaseSchema, BaseInputSchema

class FeedbackStatus(str, Enum):
    """
    Статусы обратной связи для обработки администратором

    Attributes:
        PENDING (str): Обратная связь ожидает обработки
        PROCESSED (str): Обратная связь обработана
        DELETED (str): Обратная связь удалена (холодное удаление)
    """

    PENDING = "pending"
    PROCESSED = "processed"
    DELETED = "deleted"

class FeedbackSchema(BaseSchema):
    """
    Схема обратной связи

    Attributes:
        id (int): Идентификатор обратной связи
        name (str): Имя пользователя
        phone (str | None): Телефон пользователя
        email (EmailStr): Электронная почта пользователя
        status (FeedbackStatus): Статус обратной связи
    """
    id: int
    name: str = Field(min_length=0, max_length=50, description="Имя пользователя")
    phone: str | None = Field(
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
        name (str): Имя пользователя
        phone (str | None): Телефон пользователя
        email (EmailStr): Электронная почта пользователя
        status (FeedbackStatus): Статус обратной связи (по умолчанию PENDING)
    """
    name: str = Field(min_length=0, max_length=50, description="Имя пользователя")
    phone: str | None = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )
    email: EmailStr = Field(description="Email пользователя")
    status: FeedbackStatus = FeedbackStatus.PENDING

class FeedbackUpdateSchema(BaseInputSchema):
    """
    Схема обновления обратной связи

    Attributes:
        name (str): Имя пользователя
        phone (str | None): Телефон
        email (EmailStr): Электронная почта
        status (FeedbackStatus): Статус обратной связи
    """
    name: str = Field(min_length=0, max_length=50, description="Имя пользователя")
    phone: str | None = Field(
        None,
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        description="Телефон в формате +7 (XXX) XXX-XX-XX",
        examples=["+7 (999) 123-45-67"],
    )
    email: EmailStr = Field(description="Email пользователя")
    status: FeedbackStatus

class FeedbackResponse(BaseSchema):
    """
    Схема ответа на создание обратной связи.

    Attributes:
        id (int): Идентификатор обратной связи.
        manager_id (int | None): ID менеджера, которому адресована обратная связь.
        message (str): Сообщение об успешном создании обратной связи.
    """
    id: int
    manager_id: int | None
    message: str = "Обратная связь успешно создана"

from enum import Enum
from typing import List
from pydantic import Field

from ..base import BaseInputSchema, BaseResponseSchema

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseInputSchema):
    """
    Схема сообщения для чата с AI

    Attributes:
        role: Роль отправителя сообщения
        text: Текст сообщения
    """
    role: str = Field(description="Роль отправителя сообщения")
    text: str = Field(description="Текст сообщения")


class CompletionOptions(BaseInputSchema):
    """
    Настройки генерации ответа

    Attributes:
        stream: Потоковая генерация
        temperature: Температура генерации
        maxTokens: Максимальное количество токенов
    """
    stream: bool = Field(default=False)
    temperature: float = Field(default=0.6)
    maxTokens: str = Field(default="2000")


class AIChatRequest(BaseInputSchema):
    """
    Схема запроса к AI чату

    Attributes:
        modelUri: URI модели
        completionOptions: Настройки генерации
        messages: Список сообщений
    """
    modelUri: str
    completionOptions: CompletionOptions
    messages: List[Message]


class AIChatResponse(BaseResponseSchema):
    """
    Схема ответа AI чата

    Attributes:
        text: Сгенерированный текст
        status: Статус ответа
    """
    text: str
    status: str
    success: bool = True

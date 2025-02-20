from enum import Enum
from typing import List

from pydantic import Field

from ..base import BaseInputSchema, BaseResponseSchema


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ModelType(str, Enum):
    YANDEX_GPT_LITE = "yandexgpt-lite"
    YANDEX_GPT_PRO = "yandexgpt"
    YANDEX_GPT_PRO_32K = "yandexgpt-32k"
    LLAMA_8B = "llama-lite"
    LLAMA_70B = "llama"
    CUSTOM = "custom"


class ModelVersion(str, Enum):
    DEPRECATED = "deprecated"
    LATEST = "latest"
    RC = "rc"


class ModelPricing(Enum):
    """
    Цены и юниты для разных моделей и режимов
    """

    YANDEX_GPT_LITE_SYNC = (1, 0.20)  # (юниты, цена в рублях за 1000 токенов)
    YANDEX_GPT_LITE_ASYNC = (0.5, 0.10)
    YANDEX_GPT_PRO_SYNC = (6, 1.20)
    YANDEX_GPT_PRO_ASYNC = (3, 0.60)
    DATASPHERE_SYNC = (6, 1.20)
    DATASPHERE_ASYNC = (3, 0.60)
    LLAMA_8B_SYNC = (1, 0.20)
    LLAMA_8B_ASYNC = (0.5, 0.10)
    LLAMA_70B_SYNC = (6, 1.20)
    LLAMA_70B_ASYNC = (3, 0.60)


class Message(BaseInputSchema):
    """
    Схема сообщения для чата с AI

    Attributes:
        role: Роль отправителя сообщения
        text: Текст сообщения
    """

    role: MessageRole
    text: str


class ReasoningOptions(BaseInputSchema):
    """
    Настройки рассуждений модели

    Attributes:
        mode: Режим рассуждений (DISABLED/ENABLED)
    """

    mode: str = "DISABLED"


class CompletionOptions(BaseInputSchema):
    """
    Настройки генерации ответа

    Attributes:
        stream: Потоковая генерация
        temperature: Температура генерации
        maxTokens: Максимальное количество токенов
        reasoningOptions: Настройки рассуждений
    """

    stream: bool = Field(default=False)
    temperature: float = Field(default=0.6)
    maxTokens: str = Field(default="2000")
    reasoningOptions: ReasoningOptions = Field(default_factory=ReasoningOptions)


class Alternative(BaseInputSchema):
    """
    Альтернативный ответ модели

    Attributes:
        message: Сообщение от модели
        status: Статус генерации
    """

    message: Message
    status: str


class Usage(BaseInputSchema):
    """
    Статистика использования токенов

    Attributes:
        inputTextTokens: Количество токенов во входном тексте
        completionTokens: Количество токенов в ответе
        totalTokens: Общее количество токенов
    """

    inputTextTokens: str
    completionTokens: str
    totalTokens: str


class Result(BaseInputSchema):
    """
    Результат генерации

    Attributes:
        alternatives: Список альтернативных ответов
        usage: Статистика использования
        modelVersion: Версия модели
    """

    alternatives: List[Alternative]
    usage: Usage
    modelVersion: str


class AIChatRequest(BaseInputSchema):
    """
    Схема запроса к AI чату

    Attributes:
        modelUri: URI модели
        completionOptions: Настройки генерации
        messages: Список сообщений
    """

    modelUri: str
    completionOptions: CompletionOptions = Field(default_factory=CompletionOptions)
    messages: List[Message]


class AIChatResponse(BaseResponseSchema):
    """
    Схема ответа AI чата

    Attributes:
        success: Флаг успешности запроса
        result: Результат генерации
    """

    success: bool = True
    result: Result

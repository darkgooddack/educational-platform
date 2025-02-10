"""
Модуль содержит схемы для работы с тестами, вопросами и ответами.

Схемы разделены на:
- Базовые (Base) - содержат общие поля
- Создания (Create) - для входных данных при создании
- Ответов - для возврата полных данных
- Списков - для возврата коллекций
"""

from enum import Enum
from typing import List, Optional

from ..base import (BaseInputSchema, BaseResponseSchema, CommonBaseSchema,
                    ListResponseSchema)


class QuestionType(str, Enum):
    """Типы вопросов в тесте"""

    SINGLE = "single"  # один правильный ответ
    MULTIPLE = "multiple"  # несколько правильных ответов


class TestBase(CommonBaseSchema):
    """
    Базовая схема теста с общими полями

    Attributes:
        title: Название теста
        description: Описание теста
        duration: Длительность в минутах
        passing_score: Проходной балл
        max_attempts: Максимальное количество попыток
        theme_id: ID темы теста
        video_lecture_id: ID связанной видео-лекции (опционально)
        lecture_id: ID связанной лекции (опционально)
    """

    title: str
    description: str
    duration: int
    passing_score: int
    max_attempts: int
    theme_id: int
    video_lecture_id: Optional[int] = None
    lecture_id: Optional[int] = None


class AnswerBase(CommonBaseSchema):
    """
    Базовая схема ответа на вопрос

    Attributes:
        text: Текст ответа
        is_correct: Признак правильного ответа
    """

    text: str
    is_correct: bool


class QuestionBase(CommonBaseSchema):
    """
    Базовая схема вопроса

    Attributes:
        text: Текст вопроса
        type: Тип вопроса (один/несколько правильных ответов)
        points: Количество баллов за вопрос
    """

    text: str
    type: QuestionType
    points: int = 1


# Схемы для создания
class AnswerCreateSchema(BaseInputSchema):
    """
    Схема для создания варианта ответа
    Attributes:
        text: Текст ответа
        is_correct: Признак правильного ответа
    """

    text: str
    is_correct: bool


class QuestionCreateSchema(BaseInputSchema):
    """
    Схема для создания вопроса

    Attributes:
        text: Текст вопроса
        type: Тип вопроса (один/несколько правильных ответов)
        points: Количество баллов за вопрос
        answers: Список вариантов ответов
    """

    text: str
    type: QuestionType
    points: int = 1
    answers: List[AnswerCreateSchema]


class TestCreateSchema(BaseInputSchema):
    """
    Схема для создания теста

    Attributes:
        title: Название теста
        description: Описание теста
        duration: Длительность в минутах
        passing_score: Проходной балл
        max_attempts: Максимальное количество попыток
        theme_id: ID темы теста
        video_lecture_id: ID связанной видео-лекции (опционально)
        lecture_id: ID связанной лекции (опционально)
        questions: Список вопросов теста
    """

    title: str
    description: str
    duration: int
    passing_score: int = 60
    max_attempts: int = 3
    theme_id: int
    video_lecture_id: Optional[int] = None
    lecture_id: Optional[int] = None
    questions: List[QuestionCreateSchema]


# Схемы для ответов
class AnswerSchema(AnswerBase):
    """
    Схема для возврата данных ответа

    Attributes:
        id: ID ответа
    """

    id: int


class QuestionSchema(QuestionBase):
    """
    Схема для возврата данных вопроса

    Atttributes:
        id: ID вопроса
        answers: Список вариантов ответов
    """

    id: int
    answers: List[AnswerSchema]


class TestSchema(TestBase):
    """
    Схема для возврата данных теста

    Attributes:
        id: ID теста
        questions: Список вопросов теста
    """

    id: int
    questions: List[QuestionSchema]


class TestUpdateSchema(BaseResponseSchema):
    """
    Схема для обновления теста

    Attributes:
        id: ID теста
        succes: Признак успешного обновления
        message: Сообщение об обновлении
    """

    id: int
    success: bool = True
    message: str = "Тест успешно обновлен"


class TestDeleteResponse(BaseResponseSchema):
    """
    Схема ответа при удалении теста

    Attributes:
        id: ID теста
        success: Признак успешного удаления
        message: Сообщение об удалении
    """

    id: int
    success: bool = True
    message: str = "Тест успешно удален"


class TestListResponse(BaseResponseSchema):
    """
    Схема для возврата списка тестов

    Attributes:
        items: Список тестов
        success: Признак успешного получения списка
        message: Сообщение об успешном получении списка
    """

    item: TestSchema
    success: bool = True
    message: str = "Тест успешно добавлен"

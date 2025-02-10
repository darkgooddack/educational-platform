from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TestNotFoundError
from app.models import AnswerModel, QuestionModel, TestModel
from app.schemas import (AnswerCreateSchema, PaginationParams,
                         QuestionCreateSchema, TestCreateResponse,
                         TestCreateSchema, TestDeleteResponse, TestSchema,
                         TestUpdateResponse)
from app.services import BaseService

from .data_manager import TestDataManager


class TestService(BaseService):
    """
    Сервис для работы с тестами

    Attributes:
        session (AsyncSession): Сессия для работы с базой данных
        data_manager (TestDataManager): Менеджер данных для работы с тестами

    Methods:
        create_test: Создает новый тест со всеми вопросами и ответами.
        update_test: Обновляет тест.
        delete_test: Удаляет тест.
        add_question: Добавить вопрос в тест.
        add_answer: Добавить ответ в вопрос.
        get_test_by_id: Получает тест по его ID.
        get_tests: Получает список тестов с возможностью пагинации, поиска и фильтрации.
    """

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self._data_manager = TestDataManager(session)

    async def create_test(
        self, test_data: TestCreateSchema, author_id: int
    ) -> TestCreateResponse:
        """
        Создает новый тест со всеми вопросами и ответами.

        Args:
            test_data: Данные теста
            author_id: ID автора теста

        Returns:
            TestSchema: Созданный тест
        """
        test = TestModel(
            title=test_data.title,
            description=test_data.description,
            duration=test_data.duration,
            passing_score=test_data.passing_score,
            max_attempts=test_data.max_attempts,
            theme_id=test_data.theme_id,
            video_lecture_id=test_data.video_lecture_id,
            lecture_id=test_data.lecture_id,
            author_id=author_id,
        )
        return await self._data_manager.create_test(test, test_data.questions)

    async def get_tests(
        self,
        pagination: PaginationParams,
        theme_id: Optional[int] = None,
        video_lecture_id: Optional[int] = None,
        lecture_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[TestSchema], int]:
        """
        Получает список тестов с фильтрацией.

        Args:
            pagination: Параметры пагинации
            theme_id: Фильтр по теме
            video_lecture_id: Фильтр по видео-лекции
            lecture_id: Фильтр по лекции
            search: Поисковый запрос

        Returns:
            Tuple[List[TestSchema], int]: Список тестов и общее количество
        """
        return await self._data_manager.get_tests_paginated(
            pagination=pagination,
            theme_id=theme_id,
            video_lecture_id=video_lecture_id,
            lecture_id=lecture_id,
            search=search,
        )

    async def get_test_by_id(self, test_id: int) -> TestSchema:
        """
        Получает тест по ID

        Args:
            test_id: ID теста

        Returns:
            TestSchema: Тест с указанным ID
        """
        test = await self._data_manager.get_test(test_id)
        if not test:
            raise TestNotFoundError(f"Тест с ID {test_id} не найден")
        return test

    async def add_question(
        self, test_id: int, question_data: QuestionCreateSchema
    ) -> TestSchema:
        """
        Добавляет вопрос к тесту

        Args:
            test_id: ID теста
            question_data: Данные вопроса

        Returns:
            TestSchema: Обновленный тест с добавленным вопросом
        """
        return await self._data_manager.add_question(test_id, question_data)

    async def add_answer(
        self, question_id: int, answer_data: AnswerCreateSchema
    ) -> TestSchema:
        """
        Добавляет вариант ответа к вопросу

        Args:
            question_id: ID вопроса
            answer_data: Данные ответа

        Returns:
            TestSchema: Обновленный тест с добавленным ответом
        """
        return await self._data_manager.add_answer(question_id, answer_data)

    async def update_test(self, test_id: int, test_data) -> TestUpdateResponse:
        """
        Обновляет данные теста.

        Args:
            test_id: ID теста
            test_data: Данные теста

        Returns:
            TestUpdateResponse: Схема ответа на обновление теста
        """
        return await self.test_manager.update_test(test_id, test_data)

    async def delete_test(
        self,
        test_id: int,
    ) -> TestDeleteResponse:
        """
        Удаляет теста из базы данных.

        Args:
            test_id (int): ID удаляемого теста

        Returns:
            FeedbackResponse: Схема ответа на создание обратной связи
        """
        return await self.test_manager.delete_test(test_id)

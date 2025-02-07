from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import TestSchema, TestCreateSchema, QuestionCreateSchema, AnswerCreateSchema, PaginationParams, TestListResponse
from app.models import TestModel, QuestionModel, AnswerModel
from app.services import BaseService
from app.core.exceptions import TestNotFoundError
from .data_manager import TestDataManager

class TestService(BaseService):
    """Сервис для работы с тестами"""
    
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self._data_manager = TestDataManager(session)

    async def create_test(self, test_data: TestCreateSchema, author_id: int) -> TestListResponse:
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
            author_id=author_id
        )
        return await self._data_manager.add_test(test, test_data.questions)

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
            search=search
        )

    async def get_test_by_id(self, test_id: int) -> TestSchema:
        """Получает тест по ID"""
        test = await self._data_manager.get_test(test_id)
        if not test:
            raise TestNotFoundError(f"Тест с ID {test_id} не найден")
        return test

    async def add_question(self, test_id: int, question_data: QuestionCreateSchema) -> TestSchema:
        """Добавляет вопрос к тесту"""
        return await self._data_manager.add_question(test_id, question_data)

    async def add_answer(self, question_id: int, answer_data: AnswerCreateSchema) -> TestSchema:
        """Добавляет вариант ответа к вопросу"""
        return await self._data_manager.add_answer(question_id, answer_data)
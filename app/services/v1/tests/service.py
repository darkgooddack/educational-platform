from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TestNotFoundError
from app.models import AnswerModel, QuestionModel, TestModel
from app.schemas import (AnswerCreateSchema, PaginationParams,
                         QuestionCreateSchema, TestAnswerSchema,
                         TestCatalogSchema, TestCompleteResponse,
                         TestCreateResponse, TestCreateSchema,
                         TestDeleteResponse, TestSchema, TestUpdateResponse)
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
        self.test_manager = TestDataManager(session)

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
        return await self.test_manager.create_test(test, test_data.questions)

    async def get_tests_with_all_data(
        self,
        pagination: PaginationParams,
        theme_ids: Optional[List[int]] = None,
        video_lecture_id: Optional[int] = None,
        lecture_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[TestSchema], int]:
        """
        Получает список тестов со всеми данными с фильтрацией.

        Args:
            pagination: Параметры пагинации
            theme_ids: Фильтр по темам
            video_lecture_id: Фильтр по видео-лекции
            lecture_id: Фильтр по лекции
            search: Поисковый запрос

        Returns:
            Tuple[List[TestSchema], int]: Список тестов и общее количество
        """
        return await self.test_manager.get_tests_with_all_data_paginated(
            pagination=pagination,
            theme_ids=theme_ids,
            video_lecture_id=video_lecture_id,
            lecture_id=lecture_id,
            search=search,
        )

    async def get_tests(
        self,
        pagination: PaginationParams,
        theme_ids: Optional[List[int]] = None,
        video_lecture_id: Optional[int] = None,
        lecture_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[TestCatalogSchema], int]:
        """
        Получает список тестов с фильтрацией.

        Args:
            pagination: Параметры пагинации
            theme_ids: Фильтр по темам
            video_lecture_id: Фильтр по видео-лекции
            lecture_id: Фильтр по лекции
            search: Поисковый запрос

        Returns:
            Tuple[List[TestCatalogSchema], int]: Список тестов и общее количество
        """
        return await self.test_manager.get_tests_paginated(
            pagination=pagination,
            theme_ids=theme_ids,
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
        test = await self.test_manager.get_test(test_id)
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
        return await self.test_manager.add_question(test_id, question_data)

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
        return await self.test_manager.add_answer(question_id, answer_data)

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
            TestDeleteResponse: Схема ответа на удаление теста
        """
        return await self.test_manager.delete_test(test_id)

    async def complete_test_with_answers(
        self, test_id: int, user_id: int, answers: List[TestAnswerSchema]
    ) -> TestCompleteResponse:
        """
        Обрабатывает завершение теста пользователем.

        Args:
            test_id: ID теста
            user_id: ID пользователя
            answers: Список ответов пользователя

        Returns:
            TestCompleteResponse: Результаты прохождения теста
        """
        # TODO:
        # 1. Получить тест с правильными ответами
        # 2. Проверить ответы пользователя
        # 3. Подсчитать баллы
        # 4. Сохранить результат в БД
        # 5. Обновить статистику пользователя
        # 6. Сгенерировать сертификат если нужно
        # 7. Отправить уведомление

        # Пока просто увеличиваем счетчик
        return await self.test_manager.increment_popularity(test_id)

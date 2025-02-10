"""
Модуль маршрутов для работы с тестами.

Предоставляет API эндпоинты для:
- Создания тестов
- Получения списка тестов с фильтрацией и пагинацией
- Получения теста по ID
- Добавления вопросов к тесту
- Добавления вариантов ответов к вопросам
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.schemas import (AnswerCreateSchema, Page, PaginationParams,
                         QuestionCreateSchema, TestCreateSchema,
                         TestListResponse, TestSchema, UserCredentialsSchema)
from app.services import TestService

logger = logging.getLogger(__name__)


def setup_routes(router: APIRouter):
    """Настраивает маршруты для работы с тестами"""

    @router.post("/", response_model=TestListResponse)
    async def create_test(
        test: TestCreateSchema,
        _current_user: UserCredentialsSchema = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestListResponse:
        """
        # Создание нового теста

        ## Args
        * **test** - данные для создания теста
        * **_current_user** - текущий авторизованный пользователь
        * **db_session** - сессия базы данных

        ## Returns
        * Созданный тест в виде списка с одним элементом
        """
        service = TestService(db_session)
        result = await service.create_test(test, author_id=_current_user.id)
        return result

    @router.get("/", response_model=Page[TestSchema])
    async def get_tests(
        pagination: PaginationParams = Depends(),
        theme_id: Optional[int] = Query(None, description="Фильтр по теме"),
        video_lecture_id: Optional[int] = Query(
            None, description="Фильтр по видео-лекции"
        ),
        lecture_id: Optional[int] = Query(None, description="Фильтр по лекции"),
        search: str = Query(None, description="Поиск по названию и описанию"),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> Page[TestSchema]:
        """
        # Получение списка тестов с пагинацией и фильтрацией

        ## Args
        * **pagination** - параметры пагинации (пропуск, лимит, сортировка)
        * **theme_id** - фильтр по ID темы
        * **video_lecture_id** - фильтр по ID видео-лекции
        * **lecture_id** - фильтр по ID лекции
        * **search** - поисковый запрос по названию и описанию
        * **db_session** - сессия базы данных

        ## Returns
        * Страница с тестами и метаданными пагинации
        """
        service = TestService(db_session)
        tests, total = await service.get_tests(
            pagination=pagination,
            theme_id=theme_id,
            video_lecture_id=video_lecture_id,
            lecture_id=lecture_id,
            search=search,
        )
        return Page(
            items=tests, total=total, page=pagination.page, size=pagination.limit
        )

    @router.get("/{test_id}", response_model=TestSchema)
    async def get_test(
        test_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestSchema:
        """
        # Получение теста по ID

        ## Args
        * **test_id** - ID теста для получения
        * **db_session** - сессия базы данных

        ## Returns
        * Данные теста
        """
        service = TestService(db_session)
        return await service.get_test_by_id(test_id)

    @router.post("/{test_id}/questions", response_model=TestSchema)
    async def add_question(
        test_id: int,
        question: QuestionCreateSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestSchema:
        """
        # Добавление нового вопроса к тесту

        ## Args
        * **test_id** - ID теста, к которому добавляется вопрос
        * **question** - данные создаваемого вопроса
        * **db_session** - сессия базы данных

        ## Returns
        * Обновленные данные теста с добавленным вопросом
        """
        service = TestService(db_session)
        return await service.add_question(test_id, question)

    @router.post("/questions/{question_id}/answers", response_model=TestSchema)
    async def add_answer(
        question_id: int,
        answer: AnswerCreateSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestSchema:
        """
        # Добавление нового варианта ответа к вопросу

        ## Args
        * **question_id** - ID вопроса, к которому добавляется ответ
        * **answer** - данные создаваемого варианта ответа
        * **db_session** - сессия базы данных

        ## Returns
        * Обновленные данные теста с добавленным вариантом ответа
        """
        service = TestService(db_session)
        return await service.add_answer(question_id, answer)


__all__ = ["setup_routes"]

import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, get_current_user
from app.schemas import (
    TestCreateSchema,
    TestListResponse,
    TestSchema,
    UserCredentialsSchema,
    Page,
    PaginationParams,
    QuestionCreateSchema,
    AnswerCreateSchema
)
from app.services import TestService

logger = logging.getLogger(__name__)

def setup_routes(router: APIRouter):

    @router.post("/", response_model=TestListResponse)
    async def create_test(
        test: TestCreateSchema,
        _current_user: UserCredentialsSchema = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestListResponse:
        """
        **Создание нового теста.**

        **Args**:
            test (TestCreateSchema): Данные теста
            _current_user (UserCredentialsSchema): Текущий пользователь
            db_session (AsyncSession): Сессия БД

        **Returns**:
            TestListResponse: Созданный тест
        """
        service = TestService(db_session)
        result = await service.create_test(
            test,
            author_id=_current_user.id
        )
        return result

    @router.get("/", response_model=Page[TestSchema]) 
    async def get_tests(
        pagination: PaginationParams = Depends(),
        theme_id: Optional[int] = Query(None, description="Фильтр по теме"),
        video_lecture_id: Optional[int] = Query(None, description="Фильтр по видео-лекции"),
        lecture_id: Optional[int] = Query(None, description="Фильтр по лекции"),
        search: str = Query(None, description="Поиск по названию и описанию"),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> Page[TestSchema]:
        """
        **Получение тестов с пагинацией и фильтрацией.**

        **Args**:
            pagination (PaginationParams): Параметры пагинации
            theme_id (int): ID темы для фильтрации
            video_lecture_id (int): ID видео-лекции
            lecture_id (int): ID лекции
            search (str): Поисковый запрос
            db_session (AsyncSession): Сессия БД

        **Returns**:
            Page[TestSchema]: Страница с тестами
        """
        service = TestService(db_session)
        tests, total = await service.get_tests(
            pagination=pagination,
            theme_id=theme_id,
            video_lecture_id=video_lecture_id,
            lecture_id=lecture_id,
            search=search
        )
        return Page(
            items=tests,
            total=total,
            page=pagination.page,
            size=pagination.limit
        )

    @router.get("/{test_id}", response_model=TestSchema)
    async def get_test(
        test_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestSchema:
        """Получение теста по ID"""
        service = TestService(db_session)
        return await service.get_test_by_id(test_id)

    @router.post("/{test_id}/questions", response_model=TestSchema)
    async def add_question(
        test_id: int,
        question: QuestionCreateSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestSchema:
        """Добавление вопроса к тесту"""
        service = TestService(db_session)
        return await service.add_question(test_id, question)

    @router.post("/questions/{question_id}/answers", response_model=TestSchema)
    async def add_answer(
        question_id: int,
        answer: AnswerCreateSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestSchema:
        """Добавление варианта ответа к вопросу"""
        service = TestService(db_session)
        return await service.add_answer(question_id, answer)

__all__ = ["setup_routes"]

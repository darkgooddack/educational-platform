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
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.schemas import (AnswerCreateSchema, Page, PaginationParams,
                         QuestionCreateSchema, TestAnswerSchema,
                         TestCatalogSchema, TestCompleteResponse,
                         TestCreateResponse, TestCreateSchema,
                         TestDeleteResponse, TestSchema, TestUpdateResponse,
                         UserCredentialsSchema)
from app.services import TestService

logger = logging.getLogger(__name__)


def setup_routes(router: APIRouter):
    """Настраивает маршруты для работы с тестами"""

    @router.post("/", response_model=TestCreateResponse)
    async def create_test(
        test: TestCreateSchema,
        current_user: UserCredentialsSchema = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestCreateResponse:
        """
        # Создание нового теста

        ## Args
        * **test** - данные для создания теста
        * **current_user** - текущий авторизованный пользователь (временно отключено)
        * **db_session** - сессия базы данных

        ## Returns
        * Созданный тест в виде списка с одним элементом
        """
        service = TestService(db_session)
        result = await service.create_test(test, current_user.id)
        return result

    @router.get("/all", response_model=Page[TestSchema])
    async def get_tests_with_all_data(
        pagination: PaginationParams = Depends(),
        theme_ids: Optional[List[int]] = Query(None, description="Фильтр по темам"),
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
        * **theme_ids** - фильтр по ID темы
        * **video_lecture_id** - фильтр по ID видео-лекции
        * **lecture_id** - фильтр по ID лекции
        * **search** - поисковый запрос по названию и описанию
        * **db_session** - сессия базы данных

        ## Сортировка
        * **sort_by** - по какому полю сортировать (updated_at, popularity_count)
        * **sort_desc** - сортировка по убыванию (по умолчанию сортировка по убыванию - true)

        ## Returns
        * Страница с тестами и всеми параметрами и метаданными пагинации
        """
        service = TestService(db_session)
        tests, total = await service.get_tests_with_all_data(
            pagination=pagination,
            theme_ids=theme_ids,
            video_lecture_id=video_lecture_id,
            lecture_id=lecture_id,
            search=search,
        )
        return Page(
            items=tests, total=total, page=pagination.page, size=pagination.limit
        )

    @router.get("/", response_model=Page[TestCatalogSchema])
    async def get_tests(
        pagination: PaginationParams = Depends(),
        theme_ids: Optional[List[int]] = Query(None, description="Фильтр по темам"),
        video_lecture_id: Optional[int] = Query(
            None, description="Фильтр по видео-лекции"
        ),
        lecture_id: Optional[int] = Query(None, description="Фильтр по лекции"),
        search: str = Query(None, description="Поиск по названию и описанию"),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> Page[TestCatalogSchema]:
        """
        # Получение списка тестов с пагинацией и фильтрацией

        ## Args
        * **pagination** - параметры пагинации (пропуск, лимит, сортировка)
        * **theme_ids** - фильтр по ID темы
        * **video_lecture_id** - фильтр по ID видео-лекции
        * **lecture_id** - фильтр по ID лекции
        * **search** - поисковый запрос по названию и описанию
        * **db_session** - сессия базы данных

        ## Сортировка
        * **sort_by** - по какому полю сортировать (updated_at, popularity_count)
        * **sort_desc** - сортировка по убыванию (по умолчанию сортировка по убыванию - true)

        ## Returns
        * Страница с тестами и метаданными пагинации
        """
        service = TestService(db_session)
        tests, total = await service.get_tests(
            pagination=pagination,
            theme_ids=theme_ids,
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

    @router.put("/{test_id}", response_model=TestUpdateResponse)
    async def update_test(
        test_id: int,
        test: TestCreateSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestUpdateResponse:
        """
        # Обновление существующего теста

        ## Args
        * **test_id** - ID обновляемого теста
        * **test** - новые данные теста
        * **db_session** - сессия базы данных

        ## Returns
        * Обновленный тест
        """
        service = TestService(db_session)
        return await service.update_test(test_id, test)

    @router.delete("/{test_id}", response_model=TestDeleteResponse)
    async def delete_test(
        test_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestDeleteResponse:
        """
        # Удаление теста

        ## Args
        * **test_id** - ID удаляемого теста
        * **db_session** - сессия базы данных

        ## Returns
        * Удаленный тест
        """
        service = TestService(db_session)
        return await service.delete_test(test_id)

    @router.patch("/{test_id}/complete")
    async def complete_test(
        test_id: int,
        answers: List[TestAnswerSchema],
        current_user: UserCredentialsSchema = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TestCompleteResponse:
        """
        📊 # Завершение теста и получение результатов

        ## Args
        * **test_id** - ID теста
        * **answers** - Список ответов пользователя
        * **current_user** - Текущий пользователь
        * **db_session** - Сессия базы данных

        ## Return
        TestCompleteResponse - Объект, содержащий результаты теста и статистику
        """
        # TODO: Добавить:
        # 1. Проверку ответов пользователя
        # 2. Подсчет баллов/статистики
        # 3. Сохранение результатов в БД
        # 4. Формирование детального отчета
        # 5. Обновление статистики пользователя
        # 6. Отправку уведомления о завершении
        # 7. Выдачу сертификата/бейджа при успешном прохождении

        service = TestService(db_session)
        return await service.complete_test_with_answers(
            test_id=test_id, user_id=current_user.id, answers=answers
        )


__all__ = ["setup_routes"]

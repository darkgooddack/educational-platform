from typing import List, Optional, Tuple

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (BaseAPIException, DatabaseError,
                                 QuestionNotFoundError, TestDeleteError,
                                 TestGetError, TestUpdateError)
from app.models import AnswerModel, QuestionModel, TestModel
from app.schemas import (AnswerCreateSchema, PaginationParams,
                         QuestionCreateSchema, TestCreateResponse,
                         TestCreateSchema, TestDeleteResponse, TestSchema, TestCatalogSchema,
                         TestUpdateResponse, TestCompleteResponse)
from app.services import BaseEntityManager


class TestDataManager(BaseEntityManager[TestSchema]):
    """
    Менеджер данных для работы с тестами

    Attributes:
        session (AsyncSession): Сессия для работы с базой данных
        schema (Type[TestSchema]): Схема для сериализации/десериализации данных
        model (Type[TestModel]): Модель для работы с базой данных

    Methods:
        create_test: Добавляет тест с вопросами и ответами
        add_question: Добавляет вопрос в тест
        add_answer: Добавляет ответ в вопрос
        update_test: Обновляет тест
        delete_test: Удаляет тест
        get_test: Получает тест по его ID
        get_tests_paginated: Получает список тестов с возможностью пагинации, поиска и фильтрации
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=TestSchema, model=TestModel)

    async def create_test(
        self, test: TestModel, questions: List[QuestionCreateSchema]
    ) -> TestCreateResponse:
        """
        Добавляет тест с вопросами и ответами

        Args:
            test (TestModel): Тест
            questions (List[QuestionCreateSchema]): Список вопросов

        Returns:
            TestCreateResponse: Созданный тест
        """
        test.questions = [
            QuestionModel(
                text=q.text,
                type=q.type,
                points=q.points,
                answers=[
                    AnswerModel(text=a.text, is_correct=a.is_correct) for a in q.answers
                ],
            )
            for q in questions
        ]
        created_test = await self.add_item(test)
        return TestCreateResponse(item=created_test)

    def _transform_test(item: TestModel) -> dict:
        """
        Преобразует модель теста перед валидацией схемы.
        Добавляет количество вопросов в тест.
    
        Args:
            item (TestModel): Модель теста
    
        Returns:
            dict: Словарь с данными теста и количеством вопросов
        """
        data = item.__dict__
        data['questions_count'] = len(item.questions)
        return data

    async def get_tests_paginated(
        self,
        pagination: PaginationParams,
        theme_ids: Optional[List[int]] = None,
        video_lecture_id: Optional[int] = None,
        lecture_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[TestCatalogSchema], int]:
        """
        Получает список тестов с фильтрацией

        Args:
            pagination (PaginationParams): Параметры пагинации
            theme_id (int, optional): ID темы
            video_lecture_id (int, optional): ID видеолекции
            lecture_id (int, optional): ID лекции
            search (str, optional): Строка поиска

        Returns:
            Tuple[List[TestCatalogSchema], int]: Список тестов и общее количество
        """
        query = select(self.model)

        query = query.options(
            selectinload(TestModel.questions)
        )

        if theme_ids:
            query = query.filter(self.model.theme_id.in_(theme_ids))
        if video_lecture_id:
            query = query.filter(self.model.video_lecture_id == video_lecture_id)
        if lecture_id:
            query = query.filter(self.model.lecture_id == lecture_id)
        if search:
            query = query.filter(
                or_(
                    self.model.title.ilike(f"%{search}%"),
                    self.model.description.ilike(f"%{search}%"),
                )
            )
        items, total = await self.get_paginated(
            query, 
            pagination, 
            schema=TestCatalogSchema,
            transform_func=transform_test
        )
        return items, total

    async def get_test(self, test_id: int) -> TestSchema:
        """
        Получает тест по ID

        Args:
            test_id: ID теста

        Returns:
                TestSchema: Тест с указанным ID
        """
        test = await self.get_item(test_id)
        if not test:
            raise TestGetError(f"Тест с ID {test_id} не найден")
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
        test = await self.get_test(test_id)

        question = QuestionModel(
            test_id=test_id,
            text=question_data.text,
            type=question_data.type,
            points=question_data.points,
            answers=[
                AnswerModel(text=a.text, is_correct=a.is_correct)
                for a in question_data.answers
            ],
        )

        test.questions.append(question)
        return test

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
        question = await self.session.get(QuestionModel, question_id)

        if not question:
            raise QuestionNotFoundError(
                f"Вопрос с ID {question_id} не найден", question_id
            )

        answer = AnswerModel(
            question_id=question_id,
            text=answer_data.text,
            is_correct=answer_data.is_correct,
        )

        question.answers.append(answer)
        return await self.get_test(question.test_id)

    async def update_test(
        self, test_id: int, test_data: TestCreateSchema
    ) -> TestUpdateResponse:
        """
        Обновляет тест по его ID.

        Args:
            test_id (int): ID теста, который нужно обновить.
            test_data (TestCreateSchema): Данные для обновления теста.
        Returns:
            TestUpdateResponse: Обновленный тест (ID).

        Raises:
            TestGetError: Если тест с указанным ID не найден.
            TestUpdateError: Если возникла ошибка при обновлении теста.
        """

        try:
            statement = select(self.model).where(self.model.id == test_id)
            found_test_model = await self.get_one(statement)

            if not found_test_model:
                raise TestGetError(
                    message=f"Тест с id {test_id} не найден",
                    extra={"test_id": test_id}
                )

            for field, value in test_data.model_dump().items():
                setattr(found_test_model, field, value)

            updated_test_model = self.model(**test_data.model_dump())

            updated_test = await self.update_one(
                model_to_update=found_test_model, updated_model=updated_test_model
            )

            return TestUpdateResponse(id=updated_test.id)

        except DatabaseError as db_error:
            raise TestUpdateError(
                message=str(db_error),
                extra={"context": "Ошибка при обновлении теста в базе данных"},
            ) from db_error
        except Exception as e:
            raise BaseAPIException(
                status_code=500,
                detail="Произошла непредвиденная ошибка",
                error_type="unknown_error",
                extra={
                    "context": "Неизвестная ошибка при обновлении теста",
                    "error": str(e),
                },
            ) from e

    async def delete_test(self, test_id: int) -> TestDeleteResponse:
        """
        Удаляет тест из базы данных.

        Args:
            test_id (int): ID удаляемого теста

        Returns:
            TestListResponse: Сообщение об удалении теста

        """
        try:
            statement = select(self.model).where(self.model.id == test_id)
            found_test_model = await self.get_one(statement)

            if not found_test_model:
                raise TestDeleteError(message=f"Тест с id {test_id} не найдена")

            statement = delete(self.model).where(self.model.id == test_id)
            if not await self.delete(statement):
                raise TestDeleteError(message="Не удалось удалить тест")

            return TestDeleteResponse(id=found_test_model.id)
        except Exception as e:
            raise BaseAPIException(
                status_code=500,
                detail="Произошла непредвиденная ошибка.",
                error_type="unknown_error",
                extra={
                    "context": "Неизвестная ошибка при удалении теста.",
                    "error": str(e),
                },
            ) from e

    async def increment_popularity(self, test_id: int) -> TestSchema:
        """
        Увеличивает счетчик популярности теста на 1.

        Args:
            test_id: ID теста
        Returns:
            TestCompleteResponse: Ответ с обновленным тестом
        """
        try:
            statement = select(self.model).where(self.model.id == test_id)
            found_test = await self.get_one(statement)

            if not found_test:
                raise TestNotFoundError(
                    message=f"Тест с id {test_id} не найден",
                    extra={"test_id": test_id}
                )

            found_test.popularity_count += 1

            updated_test = await self.update_one(
                model_to_update=found_test,
                updated_model=found_test
            )

            return TestCompleteResponse(item=updated_test)

        except DatabaseError as db_error:
            raise TestUpdateError(
                message=str(db_error),
                extra={"context": "Ошибка при обновлении популярности теста"}
            ) from db_error
        except Exception as e:
            raise BaseAPIException(
                status_code=500,
                detail="Произошла непредвиденная ошибка",
                error_type="unknown_error",
                extra={
                    "context": "Неизвестная ошибка при обновлении популярности теста",
                    "error": str(e)
                }
            ) from e
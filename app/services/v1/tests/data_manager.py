from typing import List, Optional, Tuple
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TestModel, QuestionModel, AnswerModel
from app.schemas import TestSchema, QuestionCreateSchema, AnswerCreateSchema, PaginationParams, TestListResponse
from app.services import BaseEntityManager
from app.core.exceptions import TestNotFoundError

class TestDataManager(BaseEntityManager[TestSchema]):
    """Менеджер данных для работы с тестами"""

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=TestSchema, model=TestModel)

    async def add_test(self, test: TestModel, questions: List[QuestionCreateSchema]) -> TestListResponse:
        """Добавляет тест с вопросами и ответами"""
        test.questions = [
            QuestionModel(
                text=q.text,
                type=q.type,
                points=q.points,
                answers=[
                    AnswerModel(text=a.text, is_correct=a.is_correct)
                    for a in q.answers
                ]
            )
            for q in questions
        ]
        created_test = await self.add_item(test)
        return TestListResponse(items=[created_test])

    async def get_tests_paginated(
        self,
        pagination: PaginationParams,
        theme_id: Optional[int] = None,
        video_lecture_id: Optional[int] = None,
        lecture_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[TestSchema], int]:
        """Получает список тестов с фильтрацией"""
        query = select(self.model)

        if theme_id:
            query = query.filter(self.model.theme_id == theme_id)
        if video_lecture_id:
            query = query.filter(self.model.video_lecture_id == video_lecture_id)
        if lecture_id:
            query = query.filter(self.model.lecture_id == lecture_id)
        if search:
            query = query.filter(
                or_(
                    self.model.title.ilike(f"%{search}%"),
                    self.model.description.ilike(f"%{search}%")
                )
            )

        return await self.get_paginated(query, pagination)

    async def get_test(self, test_id: int) -> TestSchema:
        """Получает тест по ID"""
        test = await self.get_item(test_id)
        if not test:
            raise TestNotFoundError(f"Тест с ID {test_id} не найден")
        return test

    async def add_question(self, test_id: int, question_data: QuestionCreateSchema) -> TestSchema:
        """Добавляет вопрос к тесту"""
        test = await self.get_test(test_id)

        question = QuestionModel(
            test_id=test_id,
            text=question_data.text,
            type=question_data.type,
            points=question_data.points,
            answers=[
                AnswerModel(text=a.text, is_correct=a.is_correct)
                for a in question_data.answers
            ]
        )
    
        test.questions.append(question)
        return test

    async def add_answer(self, question_id: int, answer_data: AnswerCreateSchema) -> TestSchema:
        """Добавляет вариант ответа к вопросу"""
        question = await self.session.get(QuestionModel, question_id)
        if not question:
            raise QuestionNotFoundError(f"Вопрос с ID {question_id} не найден", question_id)

        answer = AnswerModel(
            question_id=question_id,
            text=answer_data.text,
            is_correct=answer_data.is_correct
        )
    
        question.answers.append(answer)
        return await self.get_test(question.test_id)

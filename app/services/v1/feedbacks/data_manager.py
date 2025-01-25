from typing import TypeVar, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import BaseSchema, PaginationParams, FeedbackSchema, FeedbackResponse, FeedbackCreateSchema, FeedbackStatus
from app.models import BaseModel, FeedbackModel
from app.services import BaseDataManager

M = TypeVar("M", bound=BaseModel)
T = TypeVar("T", bound=BaseSchema)

class FeedbackDataManager(BaseDataManager[FeedbackSchema]):
    """
    Менеджер данных для работы с отзывами.

    Attributes:
        session (AsyncSession): Сессия для работы с базой данных
        schema (Type[T]): Схема для сериализации и десериализации данных
        model (Type[M]): Модель данных

    Methods:
        create_feedback: Создает новый отзыв.
        get_feedback: Получает отзыв по его ID.
        proccess_feedback: Обрабатывает отзыв.
        get_feedbacks: Получает список отзывов с пагинацией и фильтрацией.
        soft_delete_feedback: Удаляет отзыв мягким удалением.
        delete_feedback: Удаляет отзыв.

    TODO:
        - Добавить метод проверки существования отзыва
    """
    def __init__(self, session: AsyncSession):
        super().__init__(
                    session=session,
                    schema=FeedbackSchema,
                    model=FeedbackModel
                )

    async def create_feedback(
        self,
        feedback: FeedbackCreateSchema,
    ) -> FeedbackResponse:
        """
        Создает новый отзыв.

        Args:
            feedback (FeedbackSchema): Схема отзыва

        Returns:
            FeedbackResponse: Схема отзыва с ID
        """
        feedback_data = feedback.model_dump()
        feedback_model = FeedbackSchema(**feedback_data)
        return await self.add_one(feedback_model)

    async def get_feedback(
        self,
        feedback_id: int,
    ) -> FeedbackResponse:
        """
        Получает отзыв по его ID.

        Args:
            feedback_id (int): ID отзыва

        Returns:
            FeedbackResponse: Схема отзыва
        """
        statement = select(FeedbackModel).where(FeedbackModel.id == feedback_id)
        return await self.get_one(statement)

    async def get_feedbacks(
        self,
        pagination: PaginationParams,
        status: str = None,
        search: str = None,
    ) -> tuple[List[FeedbackResponse], int]:
        """
        Получает список отзывов с возможностью пагинации, поиска и фильтрации.

        Args:
            pagination (PaginationParams): Параметры пагинации
            status (str): Фильтрация по статусу отзыва
            search (str): Поиск по тексту отзыва

        Returns:
            tuple[List[FeedbackResponse], int]: Список отзывов и общее количество
        """
        # Создаем запрос для получения всех отзывов
        statement = select(self.model).distinct()

        # Поиск по тексту отзыва
        if search:
            statement = statement.filter(
                self.model.text.ilike(f"%{search}%")
            )

        # Фильтр по статусу
        if status:
            statement = statement.filter(self.model.status == status)

        return await self.get_paginated(statement, pagination)

    async def update_feedback_status(self, feedback_id: int, status: FeedbackStatus) -> FeedbackResponse:
        """
        Обновляет статус поста.

        Args:
            feedback_id (int): ID поста
            status (FeedbackStatus): Новый статус поста

        Returns:
            FeedbackSchema: Обновленный пост
        """
        statement = select(FeedbackModel).where(FeedbackModel.id == feedback_id)
        feedback = await self.get_one(statement)

        if not feedback:
            return None

        updated_post = FeedbackModel(id=feedback_id, status=status)
        return await self.update_one(feedback, updated_post)


    async def delete_feedback(self, feedback_id: int) -> FeedbackResponse:
        """
        Удаляет отзыв.

        Args:
            feedback_id (int): ID
            FeedbackSchema: Удаленный пост
        Returns:
            FeedbackSchema: Удаленный пост

        """
        statement = select(FeedbackModel).where(FeedbackModel.id == feedback_id)
        feedback = await self.get_one(statement)

        if not feedback:
            return None

        return await self.delete(statement)

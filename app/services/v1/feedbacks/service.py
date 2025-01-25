
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import BaseService
from app.schemas import PaginationParams, FeedbackStatus, FeedbackResponse, FeedbackCreateSchema

from .data_manager import FeedbackDataManager


class FeedbackService(BaseService):
    """
    Сервис для работы с отзывами.

    Args:
        session (AsyncSession): Сессия для работы с базой данных

    Methods:
        create_feedback: Создает новый отзыв.
        get_feedback: Получает отзыв по его ID.
        proccess_feedback: Обрабатывает отзыв.
        get_feedbacks: Получает список отзывов с пагинацией и фильтрацией.
        soft_delete_feedback: Удаляет отзыв мягким удалением.
        delete_feedback: Удаляет отзыв.
    """
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.feedback_manager = FeedbackDataManager(session)

    async def create_feedback(
        self,
        feedback: FeedbackCreateSchema,
    ) -> FeedbackResponse:
        """
        Создает новый отзыв.

        Args:
            feedback (FeedbackCreateSchema): Схема отзыва

        Returns:
            FeedbackResponse: Схема отзыва
        """
        return await self.feedback_manager.create_feedback(feedback)

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
        return await self.feedback_manager.get_feedback(feedback_id)

    async def proccess_feedback(
        self,
        feedback_id: int,
    ) -> FeedbackResponse:
        """
        Обрабатывает отзыв.

        Args:
            feedback_id (int): ID отзыва

        Returns:
            FeedbackResponse: Схема отзыва
        """
        return await self.feedback_manager.update_feedback_status(feedback_id, FeedbackStatus.PROCESSED) #? Точно передаст то, что я хочу?

    async def soft_delete_feedback(
        self,
        feedback_id: int,
    ) -> FeedbackResponse:
        """
        Удаляет отзыв мягким удалением.

        Args:
            feedback_id (int): ID отзыва

        Returns:
            FeedbackResponse: Схема отзыва
        """
        return await self.feedback_manager.update_feedback_status(feedback_id, FeedbackStatus.DELETED)

    async def delete_feedback(
        self,
        feedback_id: int,
    ) -> FeedbackResponse:
        """
        Удаляет отзыв.

        Args:
            feedback_id (int): ID отзыва

        Returns:
            FeedbackResponse: Схема отзыва
        """
        return await self.feedback_manager.delete_feedback(feedback_id)

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
        return await self.feedback_manager.get_feedbacks(
            pagination=pagination,
            status=status,
            search=search,
        )

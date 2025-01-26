from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (FeedbackCreateSchema, FeedbackResponse,
                         FeedbackSchema, FeedbackStatus, PaginationParams)
from app.services import BaseService

from .data_manager import FeedbackDataManager


class FeedbackService(BaseService):
    """
    Сервис для работы с обратной связью.

    Args:
        session (AsyncSession): Сессия для работы с базой данных

    Methods:
        create_feedback: Создает новую обратную связь.
        get_feedback: Получает обратную связь по его ID.
        proccess_feedback: Обрабатывает обратную связь.
        restore_feedback: Восстанавливает удаленную (обработанную) обратную связь.
        get_feedbacks: Получает список обратных связей с возможностью пагинации, поиска и фильтрации.
        soft_delete_feedback: Удаляет обратную связь мягким удалением.
        delete_feedback: Удаляет обратную связь из базы данных.
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
        Создает новую обратную связь.

        Args:
            feedback (FeedbackCreateSchema): Схема создания обратной связи

        Returns:
            FeedbackResponse: Схема ответа на создание обратной связи

        TODO: Подумать как сделать оповещение о новой обратной связи, это нужно делать от сюда.
        """
        return await self.feedback_manager.create_feedback(feedback)

    async def get_feedback(
        self,
        feedback_id: int,
    ) -> FeedbackSchema:
        """
        Получает обратную связь по его ID.

        Args:
            feedback_id (int): ID обратной связи

        Returns:
            FeedbackSchema: Схема обратной связи
        """
        return await self.feedback_manager.get_feedback(feedback_id)

    async def proccess_feedback(
        self,
        feedback_id: int,
    ) -> FeedbackSchema:
        """
        Обрабатывает обратнцю связь.

        Изменяет статус обратной связи на "Обработан".

        Args:
            feedback_id (int): ID обратной связи

        Returns:
            FeedbackSchema: Схема обратной связи
        """
        return await self.feedback_manager.update_feedback_status(
            feedback_id, FeedbackStatus.PROCESSED.value
        )

    async def restore_feedback(
        self,
        feedback_id: int,
    ) -> FeedbackSchema:
        """
        Восстанавливает удаленную (обработанную) обратную связь.

        Можно также использовть для возвращения обратной связи в статус "Ожидает обработки" из "Обработан", не только из "Удален".

        Изменяет статус обратной связи на "Ожидает обработки".

        Args:
            feedback_id (int): ID обратной связи

        Returns:
            FeedbackSchema: Схема обратной связи
        """
        return await self.feedback_manager.update_feedback_status(
            feedback_id, FeedbackStatus.PENDING.value
        )

    async def soft_delete_feedback(
        self,
        feedback_id: int,
    ) -> FeedbackSchema:
        """
        Удаляет обратную связь мягким удалением.

        Args:
            feedback_id (int): ID обратной связи

        Returns:
            FeedbackSchema: Схема обратной связи
        """
        return await self.feedback_manager.update_feedback_status(
            feedback_id, FeedbackStatus.DELETED.value
        )

    async def delete_feedback(
        self,
        feedback_id: int,
    ) -> FeedbackResponse:
        """
        Удаляет обратную связь из базы данных.

        Args:
            feedback_id (int): ID обратной связи

        Returns:
            FeedbackResponse: Схема ответа на создание обратной связи
        """
        return await self.feedback_manager.delete_feedback(feedback_id)

    async def get_feedbacks(
        self,
        pagination: PaginationParams,
        status: FeedbackStatus = None,
        search: str = None,
    ) -> tuple[List[FeedbackSchema], int]:
        """
        Получает список обратных связей с возможностью пагинации, поиска и фильтрации.

        Args:
            pagination (PaginationParams): Параметры пагинации
            status (FeedbackStatus): Фильтрация по статусу обратной связи
            search (str): Поиск по тексту обратной связи

        Returns:
            tuple[List[FeedbackSchema], int]: Список обратных связей и общее количество
        """
        return await self.feedback_manager.get_feedbacks(
            pagination=pagination,
            status=status,
            search=search,
        )

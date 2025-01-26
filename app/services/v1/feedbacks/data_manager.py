from typing import List, TypeVar

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (BaseAPIException, DatabaseError,
                                 FeedbackAddError)
from app.models import BaseModel, FeedbackModel
from app.schemas import (BaseSchema, FeedbackCreateSchema, FeedbackResponse,
                         FeedbackSchema, FeedbackStatus, PaginationParams)
from app.services.v1.users import UserService
from app.services.v1.base import BaseDataManager

M = TypeVar("M", bound=BaseModel)
T = TypeVar("T", bound=BaseSchema)


class FeedbackDataManager(BaseDataManager[FeedbackSchema]):
    """
    Менеджер данных для работы с обратной связью.

    Attributes:
        session (AsyncSession): Сессия для работы с базой данных
        schema (Type[T]): Схема для сериализации и десериализации данных
        model (Type[M]): Модель данных

    Methods:
        create_feedback: Создает новую обратную связь.
        get_feedback: Получает обратную связь по его ID.
        update_feedback_status: Обновляет статус обратной связи.
        get_feedbacks: Получает список обратных связей с возможностью пагинации, поиска и фильтрации.
        delete_feedback: Удаляет обратную связь из базы данных.
        exists_feedback: Проверяет, существует ли обратная связь с указанным ID.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            schema=FeedbackSchema,
            model=FeedbackModel,
        )
        self._user_service = UserService(session)

    async def create_feedback(
        self,
        feedback: FeedbackCreateSchema,
    ) -> FeedbackResponse:
        """
        Создает новую обратную связь.

        Args:
            feedback (FeedbackCreateSchema): Схема создания обратной связи.

        Returns:
            FeedbackResponse: Схема ответа на создание обратной связи.
        """
        try:

            # Проверяем, существует ли менеджер, к которому адресуется обратная связь, если нет, то адресуем всем менеджерам (None)
            if feedback.manager_id == 0:
                feedback.manager_id = None
            else:
                manager = self._user_service.exists_manager(feedback.manager_id)
                if not manager:
                    feedback.manager_id = None

            feedback_data = feedback.model_dump()
            feedback_model = self.model(**feedback_data)
            created_feedback_schema = await self.add_one(feedback_model)

            return FeedbackResponse(
                id=created_feedback_schema.id,
                manager_id=created_feedback_schema.manager_id,
                message="Обратная связь успешно отправлена!",
            )
        except DatabaseError as db_error:
            raise FeedbackAddError(
                message=str(db_error),
                extra={
                    "context": "Ошибка при добавлении обратной связи в базу данных."
                },
            ) from db_error
        except ValidationError as ve:
            raise BaseAPIException(
                status_code=400,
                detail="Ошибка валидации данных обратной связи.",
                error_type="validation_error",
                extra={"validation_errors": ve.errors()},
            ) from ve
        except Exception as e:
            raise BaseAPIException(
                status_code=500,
                detail="Произошла непредвиденная ошибка.",
                error_type="unknown_error",
                extra={
                    "context": "Неизвестная ошибка при добавлении обратной связи.",
                    "error": str(e),
                },
            ) from e

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
        statement = select(self.model).where(self.model.id == feedback_id)
        return await self.get_one(statement)

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
            tuple[List[FeedbackSchema], int]: Список обратных связией и их общее количество
        """
        statement = select(self.model).distinct()

        # Поиск по тексту
        if search:
            statement = statement.filter(self.model.text.ilike(f"%{search}%"))

        # Фильтр по статусу
        if status:
            statement = statement.filter(self.model.status == status)

        return await self.get_paginated(statement, pagination)

    async def exists_feedback(self, feedback_id: int) -> bool:
        """
        Проверяет, существует ли обратная связь с указанным ID.

         Args:
             feedback_id (int): ID обратной связи

         Returns:
             bool: True, если обратная связь существует, иначе False
        """
        statement = select(self.model).where(self.model.id == feedback_id)
        return await self.exists(statement)

    async def update_feedback_status(
        self, feedback_id: int, status: FeedbackStatus
    ) -> FeedbackSchema:
        """
        Обновляет статус обратной связи.

        Args:
            feedback_id (int): ID обратной связи
            status (FeedbackStatus): Новый статус обратной связи

        Returns:
            FeedbackSchema: Схема обратной связи с обновленным статусом, либо None если обратная связь не найдена
        """

        found_feedback_model = await self.get_feedback(feedback_id)

        if not found_feedback_model:
            return None

        updated_feedback = found_feedback_model
        updated_feedback.status = status
        return await self.update_one(found_feedback_model, updated_feedback)

    async def delete_feedback(self, feedback_id: int) -> FeedbackResponse:
        """
        Удаляет обратную связь из базы данных.

        Args:
            feedback_id (int): ID обратной связи

        Returns:
            FeedbackResponse: Сообщение об удалении обратной связи

        """

        found_feedback_model = await self.get_feedback(feedback_id)

        if not found_feedback_model:
            return None

        last_id = found_feedback_model.id
        last_manager_id = found_feedback_model.manager_id

        statement = select(self.model).where(self.model.id == feedback_id)

        if not await self.delete(statement):
            return None

        return FeedbackResponse(
            id=last_id,
            manager_id=last_manager_id,
            message="Обратная связь успешно удалена полностью!",
        )

"""
Модуль для работы с данными обратной связи.

TODO:

# Проверяем время последнего запроса
last_feedback = await self.get_one(
    select(self.model)
    .where(self.model.email == feedback.email)
    .order_by(self.model.created_at.desc())
)

if last_feedback:
    time_diff = datetime.now(timezone.utc) - last_feedback.created_at
    if time_diff.total_seconds() < 3600:  # 1 час
        raise BaseAPIException(
            status_code=400,
            detail="Слишком частые запросы. Попробуйте позже",
            error_type="rate_limit"
        )

# Добавить в FeedbackCreateSchema
email: EmailStr = Field(
    ...,
    description="Email пользователя",
    regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)
phone: str = Field(
    None,
    pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$"
)

Добавить rate limiting на уровне API через middleware.

Использовать CAPTCHA для веб-форм.
"""

from typing import List, TypeVar

from pydantic import ValidationError
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (BaseAPIException, DatabaseError,
                                 FeedbackAddError, FeedbackDeleteError,
                                 FeedbackGetError, FeedbackUpdateError)
from app.models import BaseModel, FeedbackModel
from app.schemas import (BaseSchema, FeedbackCreateSchema, FeedbackResponse,
                         FeedbackSchema, FeedbackStatus, PaginationParams)
from app.services.v1.base import BaseDataManager
from app.services.v1.users import UserService

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
            # Проверяем существование фидбека с таким email и статусом PENDING
            existing_feedback = await self.get_one(
                select(self.model).where(
                    and_(
                        self.model.email == feedback.email,
                        self.model.status == FeedbackStatus.PENDING,
                    )
                )
            )
            if existing_feedback:
                return FeedbackResponse(
                    id=existing_feedback.id,
                    manager_id=existing_feedback.manager_id,
                    message="У вас уже есть активная заявка на обратную связь.",
                )
            # Проверяем, существует ли менеджер, к которому адресуется обратная связь, если нет, 
            # то адресуем всем менеджерам (None)
            
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
        try:
            statement = select(self.model).where(self.model.id == feedback_id)
            result = await self.get_one(statement)
            if not result:
                raise FeedbackGetError(
                    message=f"Обратная связь с id {feedback_id} не найдена",
                    extra={"feedback_id": feedback_id},
                )
            return self.schema.model_validate(result)
        except Exception as e:
            raise BaseAPIException(
                status_code=500,
                detail="Произошла непредвиденная ошибка.",
                error_type="unknown_error",
                extra={
                    "context": "Неизвестная ошибка при получении обратной связи.",
                    "error": str(e),
                },
            ) from e

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
        try:
            statement = select(self.model).distinct()

            # Поиск по тексту
            if search:
                statement = statement.filter(self.model.text.ilike(f"%{search}%"))

            # Фильтр по статусу
            if status:
                statement = statement.filter(self.model.status == status)

            return await self.get_paginated(statement, pagination)
        except Exception as e:
            raise BaseAPIException(
                status_code=500,
                detail="Произошла непредвиденная ошибка.",
                error_type="unknown_error",
                extra={
                    "context": "Неизвестная ошибка при получении списка обратной связи.",
                    "error": str(e),
                },
            ) from e

    async def exists_feedback(self, feedback_id: int) -> bool:
        """
        Проверяет, существует ли обратная связь с указанным ID.

         Args:
             feedback_id (int): ID обратной связи

         Returns:
             bool: True, если обратная связь существует, иначе False
        """
        try:
            statement = select(self.model).where(self.model.id == feedback_id)
            return await self.exists(statement)
        except Exception as e:
            raise BaseAPIException(
                status_code=500,
                detail="Произошла непредвиденная ошибка.",
                error_type="unknown_error",
                extra={
                    "context": "Неизвестная ошибка при поиске существующей обратной связи.",
                    "error": str(e),
                },
            ) from e

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
        try:
            statement = select(self.model).where(self.model.id == feedback_id)
            found_feedback_model = await self.get_one(statement)

            if not found_feedback_model:
                raise FeedbackGetError(
                    message=f"Обратная связь с id {feedback_id} не найдена",
                    extra={"feedback_id": feedback_id},
                )

            found_feedback_model.status = status

            return await self.update_one(
                model_to_update=found_feedback_model, updated_model=found_feedback_model
            )
        except DatabaseError as db_error:
            raise FeedbackUpdateError(
                message=str(db_error),
                extra={
                    "context": "Ошибка при обновлении обратной связи в базе данных."
                },
            ) from db_error
        except Exception as e:
            raise BaseAPIException(
                status_code=500,
                detail="Произошла непредвиденная ошибка.",
                error_type="unknown_error",
                extra={
                    "context": "Неизвестная ошибка при обновлении обратной связи.",
                    "error": str(e),
                },
            ) from e

    async def delete_feedback(self, feedback_id: int) -> FeedbackResponse:
        """
        Удаляет обратную связь из базы данных.

        Args:
            feedback_id (int): ID обратной связи

        Returns:
            FeedbackResponse: Сообщение об удалении обратной связи

        """
        try:
            statement = select(self.model).where(self.model.id == feedback_id)
            found_feedback = await self.get_one(statement)

            if not found_feedback:
                raise FeedbackDeleteError(
                    message=f"Обратная связь с id {feedback_id} не найдена"
                )

            statement = delete(self.model).where(self.model.id == feedback_id)
            if not await self.delete(statement):
                raise FeedbackDeleteError(message="Не удалось удалить обратную  связь")

            return FeedbackResponse(
                id=found_feedback.id,
                manager_id=found_feedback.manager_id,
                message="Обратная связь успешно удалена!",
            )
        except Exception as e:
            raise BaseAPIException(
                status_code=500,
                detail="Произошла непредвиденная ошибка.",
                error_type="unknown_error",
                extra={
                    "context": "Неизвестная ошибка при удалении обратной связи.",
                    "error": str(e),
                },
            ) from e

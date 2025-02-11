from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.schemas import (FeedbackCreateSchema, FeedbackCreateResponse, 
                        FeedbackUpdateResponse, FeedbackDeleteResponse,
                        FeedbackSchema, FeedbackStatus, Page,
                        PaginationParams)
from app.services import FeedbackService


def setup_routes(router: APIRouter):
    @router.post("/", response_model=FeedbackCreateResponse)
    async def create_feedback(
        feedback: FeedbackCreateSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> FeedbackCreateResponse:
        """
        Создание отзыва со статусом "Ожидает обработки"

        Присвоение статуса FeedbackStatus.PENDING (по умолчанию)

        **Args**:
            feedback (FeedbackCreateSchema): Данные отзыва для создания.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            FeedbackCreateResponse: Созданный отзыв.
        """
        return await FeedbackService(db_session).create_feedback(feedback)

    @router.get("/", response_model=Page[FeedbackSchema])
    async def get_feedbacks(
        pagination: PaginationParams = Depends(),
        status: FeedbackStatus = None,
        search: str = None,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> Page[FeedbackSchema]:
        """
        **Получение всех отзывов с пагинацией, фильтрацией и поиском.**

        **Args**:
            - pagination (PaginationParams): Параметры пагинации.
            - status (FeedbackStatus): Статус отзыва для фильтрации.
            - search (str): Строка поиска по тексту отзыва.
            - db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            - Page[FeedbackSchema]: Страница с отзывами.


        """
        feedbacks, total = await FeedbackService(db_session).get_feedbacks(
            pagination=pagination,
            status=status,
            search=search,
        )
        return Page(
            items=feedbacks, total=total, page=pagination.page, size=pagination.limit
        )

    @router.get("/{feedback_id}", response_model=FeedbackSchema)
    async def get_feedback(
        feedback_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> FeedbackSchema:
        """
        Получение отзыва по идентификатору.
        Для открытия отзыва чтобы посмотреть его в полном объеме.
        Можно подгрузить данные по существующему пользователю.

        TODO:
        - Добавить проверку на принадлежность отзыва пользователю
        - Вывод дополнительной информации,
        если пользователь существует в базе данных

        **Args**:
            feedback_id (int): Идентификатор отзыва.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            FeedbackSchema: Отзыв.
        """
        return await FeedbackService(db_session).get_feedback(feedback_id)

    @router.patch("/{feedback_id}/process", response_model=FeedbackUpdateResponse)
    async def process_feedback(
        feedback_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> FeedbackUpdateResponse:
        """
        Обработка отзыва. Изменение статуса отзыва на "Обработан".

        Присвоение статуса FeedbackStatus.PROCESSING

        **Args**:
            feedback_id (int): Идентификатор отзыва.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            FeedbackUpdateResponse: Обработанный отзыв.
        """
        return await FeedbackService(db_session).proccess_feedback(feedback_id)

    @router.patch("/{feedback_id}/delete", response_model=FeedbackUpdateResponse)
    async def soft_delete_feedback(
        feedback_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> FeedbackUpdateResponse:
        """
        Мягкое удаление отзыва (изменение статуса на "Удален").

        Присвоение статуса FeedbackStatus.DELETED

        **Args**:
            feedback_id (int): Идентификатор отзыва.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            FeedbackUpdateResponse: Удаленный отзыв.
        """
        return await FeedbackService(db_session).soft_delete_feedback(feedback_id)

    @router.delete("/{feedback_id}", response_model=FeedbackDeleteResponse)
    async def delete_feedback(
        feedback_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> FeedbackDeleteResponse:
        """
        Удаление отзыва (полное удаление).

        **Args**:
            feedback_id (int): Идентификатор отзыва.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            FeedbackDeleteResponse: Удаленный отзыв.
        """
        return await FeedbackService(db_session).delete_feedback(feedback_id)


__all__ = ["setup_routes"]

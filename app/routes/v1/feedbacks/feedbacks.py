from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session
from app.schemas import PaginationParams, Page, FeedbackCreateSchema, FeedbackResponse
from app.services import FeedbackService

def setup_routes(router: APIRouter):
    @router.post("/", response_model=FeedbackResponse)
    async def create_feedback(
        feedback: FeedbackCreateSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> FeedbackResponse:
        """
        Создание отзыва со статусом "Ожидает обработки"

        Присвоение статуса FeedbackStatus.PENDING (по умолчанию)

        **Args**:
            feedback (FeedbackCreateSchema): Данные отзыва для создания.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            FeedbackResponse: Созданный отзыв.
        """
        return await FeedbackService(db_session).create_feedback(feedback)


    @router.get("/", response_model=list[FeedbackResponse])
    async def get_feedbacks(
        pagination: PaginationParams = Depends(),
        status: str = None,
        search: str = None,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> list[FeedbackResponse]:
        """
        Получение всех отзывов с пагинацией, фильтрацией и поиском.

        Args:
            pagination (PaginationParams): Параметры пагинации.
            status (str): Статус отзыва для фильтрации.
            search (str): Строка поиска по тексту отзыва.
            db_session (AsyncSession): Асинхронная сессия базы данных.

        Returns:
            Page[FeedbackResponse]: Страница с отзывами.

        **Args**:
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            list[FeedbackResponse]: Список отзывов.


        """
        feedbacks, total = await FeedbackService(db_session).get_feedbacks(
            pagination=pagination,
            status=status,
            search=search,
        )
        return Page(
            items=feedbacks,
            total=total,
            page=pagination.page,
            size=pagination.limit
        )


    @router.get("/{feedback_id}", response_model=FeedbackResponse)
    async def get_feedback(
        feedback_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> FeedbackResponse:
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
            FeedbackResponse: Отзыв.
        """
        return await FeedbackService(db_session).get_feedback(feedback_id)


    @router.put("/{feedback_id}/process", response_model=FeedbackResponse)
    async def process_feedback(
        feedback_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> FeedbackResponse:
        """
        Обработка отзыва. Изменение статуса отзыва на "Обработан".

        Присвоение статуса FeedbackStatus.PROCESSING

        **Args**:
            feedback_id (int): Идентификатор отзыва.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            FeedbackResponse: Обработанный отзыв.
        """
        return await FeedbackService(db_session).proccess_feedback(feedback_id)


    @router.put("/{feedback_id}/delete", response_model=FeedbackResponse)
    async def soft_delete_feedback(
        feedback_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> FeedbackResponse:
        """
        Мягкое удаление отзыва (изменение статуса на "Удален").

        Присвоение статуса FeedbackStatus.DELETED

        **Args**:
            feedback_id (int): Идентификатор отзыва.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            FeedbackResponse: Удаленный отзыв.
        """
        return await FeedbackService(db_session).soft_delete_feedback(feedback_id)


    @router.delete("/{feedback_id}", response_model=FeedbackResponse)
    async def delete_feedback(
        feedback_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> FeedbackResponse:
        """
        Удаление отзыва (полное удаление).

        **Args**:
            feedback_id (int): Идентификатор отзыва.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            FeedbackResponse: Удаленный отзыв.
        """
        return await FeedbackService(db_session).delete_feedback(feedback_id)



__all__ = ["setup_routes"]

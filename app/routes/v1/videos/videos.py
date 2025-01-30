from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.schemas import VideoLectureSchema, Page, PaginationParams
from app.services import VideoLectureService


def setup_routes(router: APIRouter):

    @router.get("/", response_model=Page[VideoLectureSchema])
    async def get_videos(
        pagination: PaginationParams = Depends(),
        theme: str = None,
        search: str = None,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> Page[VideoLectureSchema]:
        """
        **Получение видео лекций с пагинацией, фильтрацией и поиском.**

        **Args**:
            - pagination (PaginationParams): Параметры пагинации.
            - theme (str): Фильтр по тематике
            - search (str): Поиск по названию и описанию
            - db_session (AsyncSession): Сессия базы данных.
            - sort_by: Доступные значения (views, updated_at)
            
        **Returns**:
            - Page[VideoLectureSchema]: Страница с видео лекциями.
        """
        videos, total = await VideoLectureService(db_session).get_videos(
            pagination=pagination,
            theme=theme,
            search=search,
        )
        return Page(
            items=videos, total=total, page=pagination.page, size=pagination.limit
        )


__all__ = ["setup_routes"]

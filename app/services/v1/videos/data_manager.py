from typing import Optional, List

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import VideoLectureModel
from app.schemas import PaginationParams, VideoLectureSchema
from app.services import BaseEntityManager


class VideoLectureDataManager(BaseEntityManager[VideoLectureSchema]):
    """
    Менеджер данных для работы с видео лекциями в БД.

    Реализует низкоуровневые операции для работы с видео лекциями.

    Attributes:
        session (AsyncSession): Асинхронная сессия БД
        schema (Type[VideoLectureSchema]): Схема сериализации данных
        model (Type[VideoLectureModel]): Модель пользователя

    """

    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session, schema=VideoLectureSchema, model=VideoLectureModel
        )

    async def get_videos(
        self,
        pagination: PaginationParams,
        theme_ids: Optional[List[int]] = None,
        search: str = None,
    ) -> tuple[List[VideoLectureSchema], int]:
        """
        Получает список пользователей с возможностью пагинации, поиска и фильтрации.

        Args:
            pagination (PaginationParams): Параметры пагинации
            theme_ids (List[int]): Фильтрация по роли пользователя
            search (str): Поиск по тексту пользователя

        Returns:
            tuple[List[VideoLectureSchema], int]: Список пользователей и их общее количество
        """
        query = select(self.model).distinct()

        # Поиск по названию и описанию
        if search:
            query = query.filter(
                or_(
                    self.model.title.ilike(f"%{search}%"),
                    self.model.description.ilike(f"%{search}%"),
                )
            )

        # Фильтр по теме
        if theme_ids:
            query = query.filter(self.model.theme_id.in_(theme_ids))

        items, total = await self.get_paginated(
            query,
            pagination,
            schema=VideoLectureSchema
        )

        return items, total

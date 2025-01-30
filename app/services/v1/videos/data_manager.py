from typing import Any, List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import VideoLectureModel
from app.schemas import PaginationParams, VideoLectureSchema
from app.services import BaseEntityManager


class UserDataManager(BaseEntityManager[VideoLectureSchema]):
    """
    Менеджер данных для работы с видео лекциями в БД.

    Реализует низкоуровневые операции для работы с видео лекциями.

    Attributes:
        session (AsyncSession): Асинхронная сессия БД
        schema (Type[VideoLectureSchema]): Схема сериализации данных
        model (Type[VideoLectureModel]): Модель пользователя

    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=VideoLectureSchema, model=VideoLectureModel)

    async def get_videos(
        self,
        pagination: PaginationParams,
        theme: str = None,
        search: str = None,
    ) -> tuple[List[VideoLectureSchema], int]:
        """
        Получает список пользователей с возможностью пагинации, поиска и фильтрации.

        Args:
            pagination (PaginationParams): Параметры пагинации
            theme (str): Фильтрация по роли пользователя
            search (str): Поиск по тексту пользователя

        Returns:
            tuple[List[VideoLectureSchema], int]: Список пользователей и их общее количество
        """
        statement = select(self.model).distinct()

        # Поиск по названию и описанию
        if search:
            search_filter = (
                self.model.title.ilike(f"%{search}%") |
                self.model.description.ilike(f"%{search}%")
            )
            statement = statement.filter(search_filter)

        # Фильтр по тебе
        if theme:
            statement = statement.filter(self.model.theme == theme)

        return await self.get_paginated(statement, pagination)


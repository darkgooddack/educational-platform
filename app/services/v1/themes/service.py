from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ThemeNotFoundError
from app.models import ThemeModel
from app.schemas import (PaginationParams, ThemeCreateSchema, ThemeSchema, 
                        ThemeCreateResponse, ThemeUpdateResponse, ThemeDeleteResponse, 
                        ThemeListResponse, ThemeSelectResponse, ThemeTreeResponse)
from app.services import BaseService

from .data_manager import ThemeDataManager


class ThemeService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.theme_manager = ThemeDataManager(session)

    async def create_theme(self, theme_data: ThemeCreateSchema) -> ThemeCreateResponse:
        """
        Создает новую тему.

        Args:
            theme_data: Данные для создания темы

        Returns:
            ThemeSchema: Созданная тема
        """
        theme = ThemeModel(
            name=theme_data.name,
            description=theme_data.description,
            parent_id=theme_data.parent_id,
        )
        return await self.theme_manager.add_theme(theme)

    async def get_themes(self) -> ThemeSelectResponse:
        """
        Получает плоский список всех тем без пагинации.

        Returns:
            ThemeSelectResponse: Полный список тем
        """
        themes = await self.theme_manager.get_themes()
        return ThemeSelectResponse(items=themes)

    async def get_themes_paginated(
        self,
        pagination: PaginationParams,
        parent_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> ThemeListResponse:
        """
        Получает список тем с возможностью пагинации, поиска и фильтрации.

        Args:
            pagination: Параметры пагинации
            parent_id: Фильтр по родительской теме
            search: Поиск по названию и описанию

        Returns:
            ThemeListResponse: Список тем и общее количество
        """
        themes, total = await self.theme_manager.get_themes_paginated(
            pagination=pagination,
            parent_id=parent_id,
            search=search,
        )
        return ThemeListResponse(
            items=themes,
            total=total,
            page=pagination.page,
            size=pagination.limit
        )

    async def get_theme_by_id(self, theme_id: int) -> ThemeSchema:
        """
        Получает тему по ID.

        Args:
            theme_id: ID темы

        Returns:
            ThemeSchema: Найденная тема

        Raises:
            ThemeNotFoundError: Если тема не найдена
        """
        theme = await self.theme_manager.get_theme(theme_id)
        if not theme:
            raise ThemeNotFoundError(f"Тема с ID {theme_id} не найдена")
        return theme

    async def get_themes_tree(self) -> ThemeTreeResponse:
        """
        Получает дерево тем.

        Returns:
            ThemeTreeResponse: Список корневых тем с их дочерними темами
        """
        themes = await self.theme_manager.get_themes_tree()
        return ThemeTreeResponse(items=themes)

    async def update_theme(self, theme_id: int, theme: ThemeCreateSchema) -> ThemeUpdateResponse:
        """
        Обновляет тему.

        Args:
            theme_id (int): ID темы
            theme (ThemeCreateSchema): Новые данные темы

        Returns:
            ThemeUpdateResponse: Схема ответа на обновление темы
        """
        return await self.theme_manager.update_theme(theme_id, theme)

    async def delete_theme(self, theme_id: int) -> ThemeDeleteResponse:
        """
        Удаляет тему.

        Args:
            theme_id (int): ID темы

        Returns:
            ThemeDeleteResponse: Схема ответа на удаление темы
        """
        return await self.theme_manager.delete_theme(theme_id)
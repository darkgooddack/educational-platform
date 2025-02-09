from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ThemeNotFoundError
from app.models import ThemeModel
from app.schemas import PaginationParams, ThemeCreateSchema, ThemeSchema
from app.services import BaseService

from .data_manager import ThemeDataManager


class ThemeService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self._data_manager = ThemeDataManager(session)

    async def get_themes(self) -> List[ThemeSchema]:
        """
        Получает плоский список всех тем без пагинации.

        Returns:
            List[ThemeSchema]: Полный список тем
        """
        return await self._data_manager.get_themes()

    async def get_themes_paginated(
        self,
        pagination: PaginationParams,
        parent_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> tuple[List[ThemeSchema], int]:
        """
        Получает список тем с возможностью пагинации, поиска и фильтрации.

        Args:
            pagination: Параметры пагинации
            parent_id: Фильтр по родительской теме
            search: Поиск по названию и описанию

        Returns:
            tuple[List[ThemeSchema], int]: Список тем и общее количество
        """
        return await self._data_manager.get_themes_paginated(
            pagination=pagination,
            parent_id=parent_id,
            search=search,
        )

    async def create_theme(self, theme_data: ThemeCreateSchema) -> ThemeSchema:
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
        return await self._data_manager.add_theme(theme)

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
        theme = await self._data_manager.get_theme(theme_id)
        if not theme:
            raise ThemeNotFoundError(f"Тема с ID {theme_id} не найдена")
        return theme

    async def get_themes_tree(self) -> List[ThemeSchema]:
        """
        Получает дерево тем.

        Returns:
            List[ThemeSchema]: Список корневых тем с их дочерними темами
        """
        return await self._data_manager.get_themes_tree()

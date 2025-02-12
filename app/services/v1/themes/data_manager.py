from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ThemeExistsError, ThemeNotFoundError
from app.models import ThemeModel
from app.schemas import (PaginationParams, ThemeSchema, ThemeCreateSchema, 
                        ThemeCreateResponse, ThemeUpdateResponse, ThemeDeleteResponse)
from app.services import BaseDataManager


class ThemeDataManager(BaseDataManager):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=ThemeSchema, model=ThemeModel)

    async def add_theme(self, theme: ThemeModel) -> ThemeCreateResponse:
        """
        Добавляет новую тему с проверкой на существование.

        Args:
            theme: Модель темы для добавления

        Returns:
            ThemeCreateResponse: Добавленная тема

        Raises:
            ThemeExistsError: Если тема с таким названием уже существует
        """
        existing_theme = await self.session.execute(
            select(self.model).where(self.model.name == theme.name)
        )
        if existing_theme.scalar_one_or_none():
            raise ThemeExistsError(theme.name)

        created_theme = await self.add_one(theme)
        return ThemeCreateResponse(item=created_theme)

    async def get_themes(self) -> List[ThemeSchema]:
        """
        Получает все темы без пагинации.

        Returns:
            List[ThemeSchema]: Полный список тем
        """
        query = select(self.model)
        result = await self.session.execute(query)
        themes = result.scalars().all()

        if not themes:
            return []
        return [self.schema.from_orm(theme) for theme in themes]

    async def get_themes_paginated(
        self,
        pagination: PaginationParams,
        parent_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> tuple[List[ThemeSchema], int]:
        """
        Получает список тем с пагинацией и фильтрацией.

        Args:
            pagination: Параметры пагинации
            parent_id: Фильтр по родительской теме
            search: Поиск по названию и описанию

        Returns:
            tuple[List[ThemeSchema], int]: Список тем и общее количество
        """
        query = select(self.model)

        if parent_id is not None:
            query = query.filter(self.model.parent_id == parent_id)

        if search:
            query = query.filter(
                or_(
                    self.model.name.ilike(f"%{search}%"),
                    self.model.description.ilike(f"%{search}%"),
                )
            )

        return await self.get_paginated(query, pagination)

    async def get_theme(self, theme_id: int) -> Optional[ThemeSchema]:
        """
        Получает тему по ID с проверкой существования.

        Args:
            theme_id: ID темы

        Returns:
            Optional[ThemeSchema]: Найденная тема

        Raises:
            ThemeNotFoundError: Если тема не найдена
        """
        theme = await self.get_one(select(self.model).filter(self.model.id == theme_id))
        if not theme:
            raise ThemeNotFoundError(f"Тема с ID {theme_id} не найдена", theme_id)
        return theme

    async def get_themes_tree(self) -> List[ThemeSchema]:
        """
        Получает полное дерево тем.
        """
        # Сначала получим ВСЕ темы одним запросом
        query = select(self.model)
        result = await self.session.execute(query)
        all_themes = result.scalars().all()

        # Создадим словарь {id: тема} для быстрого поиска
        themes_dict = {
            theme.id: ThemeSchema.model_validate(theme) for theme in all_themes
        }

        # Строим дерево
        tree = []
        for theme_id, theme in themes_dict.items():
            if theme.parent_id is None:
                # Корневые темы идут в результат
                tree.append(theme)
            else:
                # Дочерние темы добавляем к родителям
                parent = themes_dict.get(theme.parent_id)
                if parent:
                    if not hasattr(parent, "children"):
                        parent.children = []
                    parent.children.append(theme)

        return tree

    async def get_child_themes(self, parent_id: int) -> List[ThemeSchema]:
        """
        Получает дочерние темы.

        Args:
            parent_id: ID родительской темы

        Returns:
            List[ThemeSchema]: Список дочерних тем
        """
        query = select(self.model).filter(self.model.parent_id == parent_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_theme(self, theme_id: int, theme_data: ThemeCreateSchema) -> ThemeUpdateResponse:
        """Обновляет тему в базе данных"""
        theme = await self.get_theme(theme_id)
        updated = await self.update_one(theme_id, theme_data)
        return ThemeUpdateResponse(id=theme_id)

    async def delete_theme(self, theme_id: int) -> ThemeDeleteResponse:
        """Удаляет тему из базы данных"""
        theme = await self.get_theme(theme_id)
        await self.delete_one(theme_id)
        return ThemeDeleteResponse(id=theme_id)
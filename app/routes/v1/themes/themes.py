from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.schemas import ThemeSchema, ThemeCreateSchema, ListResponseSchema, Page, PaginationParams
from app.services import ThemeService

def setup_routes(router: APIRouter):

    @router.get("/all", response_model=ListResponseSchema[ThemeSchema])
    async def get_all_themes(
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ListResponseSchema[ThemeSchema]:
        """Получение полного списка тем без пагинации"""
        service = ThemeService(db_session)
        themes = await service.get_themes()
        return ListResponseSchema(
            success=True,
            message="Темы успешно получены",
            items=themes
        )

    @router.get("", response_model=ListResponseSchema[ThemeSchema])
    async def get_themes_paginated(
        pagination: PaginationParams = Depends(),
        parent_id: int = Query(None, description="ID родительской темы"),
        search: str = Query(None, description="Поиск по названию и описанию"),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ListResponseSchema[ThemeSchema]:
        """Получение списка тем с фильтрацией"""
        service = ThemeService(db_session)
        themes, total = await service.get_themes_paginated(
            pagination=pagination,
            parent_id=parent_id,
            search=search
        )
        return ListResponseSchema(
            success=True,
            message="Темы успешно получены",
            items=themes,
            total=total
        )

    @router.get("", response_model=ListResponseSchema[ThemeSchema])
    async def get_themes(
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ListResponseSchema[ThemeSchema]:
        """Получение списка всех тем"""
        service = ThemeService(db_session)
        themes = await service.get_themes()
        return ListResponseSchema(
            success=True,
            message="Темы успешно получены",
            items=themes
        )

    @router.get("/tree", response_model=List[ThemeSchema])
    async def get_themes_tree(
        db_session: AsyncSession = Depends(get_db_session),
    ) -> List[ThemeSchema]:
        """Получение дерева тем"""
        service = ThemeService(db_session)
        return await service.get_themes_tree()

    @router.get("/{theme_id}", response_model=ThemeSchema)
    async def get_theme(
        theme_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ThemeSchema:
        """Получение темы по ID"""
        service = ThemeService(db_session)
        return await service.get_theme_by_id(theme_id)

    @router.post("", response_model=ThemeSchema)
    async def create_theme(
        theme: ThemeCreateSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ThemeSchema:
        """Создание новой темы"""
        service = ThemeService(db_session)
        return await service.create_theme(theme)

__all__ = ["setup_routes"]
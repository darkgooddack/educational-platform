from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.schemas import (ListResponseSchema, Page, PaginationParams,
                         ThemeCreateResponse, ThemeCreateSchema,
                         ThemeDeleteResponse, ThemeListResponse, ThemeSchema,
                         ThemeSelectResponse, ThemeTreeResponse,
                         ThemeUpdateResponse)
from app.services import ThemeService


def setup_routes(router: APIRouter):

    @router.post("", response_model=ThemeCreateResponse)
    async def create_theme(
        theme: ThemeCreateSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ThemeCreateResponse:
        """Создание новой темы"""
        service = ThemeService(db_session)
        return await service.create_theme(theme)

    @router.get("/paginated", response_model=ThemeListResponse)
    async def get_themes_paginated(
        pagination: PaginationParams = Depends(),
        parent_id: int = Query(None, description="ID родительской темы"),
        search: str = Query(None, description="Поиск по названию и описанию"),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ThemeListResponse:
        """Получение списка тем с фильтрацией"""
        service = ThemeService(db_session)
        page = await service.get_themes_paginated(
            pagination=pagination, parent_id=parent_id, search=search
        )
        return ThemeListResponse(
            items=page.items,
            total=page.total,
            page=page.page,
            size=page.size,
        )

    @router.get("", response_model=ThemeSelectResponse)
    async def get_themes(
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ThemeSelectResponse:
        """Получение списка всех тем"""
        service = ThemeService(db_session)
        return await service.get_themes()

    @router.get("/tree", response_model=ThemeTreeResponse)
    async def get_themes_tree(
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ThemeTreeResponse:
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
        theme = await service.get_theme_by_id(theme_id)
        return theme

    @router.put("/{theme_id}", response_model=ThemeUpdateResponse)
    async def update_theme(
        theme_id: int,
        theme: ThemeCreateSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ThemeUpdateResponse:
        """
        # Обновление существующей темы

        ## Args
        * **theme_id** - ID обновляемой темы
        * **theme** - новые данные темы
        * **db_session** - сессия базы данных

        ## Returns
        * Обновленная тема
        """
        service = ThemeService(db_session)
        return await service.update_theme(theme_id, theme)

    @router.delete("/{theme_id}", response_model=ThemeDeleteResponse)
    async def delete_theme(
        theme_id: int,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> ThemeDeleteResponse:
        """
        # Удаление темы

        ## Args
        * **theme_id** - ID удаляемой темы
        * **db_session** - сессия базы данных

        ## Returns
        * Удаленная тема
        """
        service = ThemeService(db_session)
        return await service.delete_theme(theme_id)


__all__ = ["setup_routes"]

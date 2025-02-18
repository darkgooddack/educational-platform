from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.core.storages.redis.auth import AuthRedisStorage
from app.schemas import (ManagerSelectSchema, Page, PaginationParams, UserRole,
                         UserSchema, UserUpdateSchema, UserStatusResponseSchema)
from app.services import UserService


def setup_routes(router: APIRouter):

    @router.get("/", response_model=Page[UserSchema])
    async def get_users(
        pagination: PaginationParams = Depends(),
        role: UserRole = Query(None, description="Фильтрация по роли пользователя"),
        search: str = Query(None, description="Поиск по данным пользователя"),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> Page[UserSchema]:
        """
        **Получение всех пользователей с пагинацией, фильтрацией и поиском.**

        **Args**:
            - pagination (PaginationParams): Параметры пагинации.
            - role (UserRole): Статус отзыва для фильтрации.
            - search (str): Строка поиска по тексту отзыва.
            - db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            - Page[UserSchema]: Страница с пользователями.


        """
        users, total = await UserService(db_session).get_users(
            pagination=pagination,
            role=role,
            search=search,
        )
        return Page(
            items=users, total=total, page=pagination.page, size=pagination.limit
        )

    @router.post("/toggle_active", response_model=UserUpdateSchema)
    async def toggle_active(
        user_id: int,
        is_active: bool,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> UserUpdateSchema:
        """
        Активация/деактивация пользователя.

        Args:
            user_id (int): Идентификатор пользователя
            is_active (bool): Статус активности
            db_session (AsyncSession): Сессия базы данных

        Returns:
            UserUpdateSchema: Обновленные данные пользователя
        """
        return await UserService(db_session).toggle_active(user_id, is_active)

    @router.post("/assign_role", response_model=UserUpdateSchema)
    async def create_user(
        user_id: int,
        role: UserRole,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> UserUpdateSchema:
        """
        Присвоение роли пользователю.

        **Args**:
            user_id (int): Идентификатор пользователя.
            role (UserRole): Роль для присвоения.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            UserUpdateSchema: Схема обновления данных пользователя.
        """
        return await UserService(db_session).assign_role(user_id, role)

    @router.get("/managers", response_model=List[ManagerSelectSchema])
    async def get_managers(
        db_session: AsyncSession = Depends(get_db_session),
    ) -> List[ManagerSelectSchema]:
        """
        Получение списка менеджеров для формы обратной связи.

        **Args**:
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            List[UserUpdateSchema]: Список менеджеров.
        """
        return await UserService(db_session).get_managers()


    @router.get("/users/{user_id}/status", response_model=UserStatusResponseSchema)
    async def get_user_status(user_id: int) -> UserStatusResponseSchema:
        """
        Получение статуса пользователя.
        **Args**:
            user_id (int): Идентификатор пользователя.

        **Returns**:
            UserStatusResponseSchema: Статус пользователя.
        """
        redis = AuthRedisStorage()
        is_online = await redis.get_online_status(user_id)
        last_activity = await redis.get_last_activity(f"token:{user_id}")

        return UserStatusResponseSchema(
            is_online=is_online,
            last_activity=last_activity
        )

__all__ = ["setup_routes"]

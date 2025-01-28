from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.schemas import UserSchema, ManagerSelectSchema, UserRole, UserUpdateSchema, Page, PaginationParams
from app.services import UserService


def setup_routes(router: APIRouter):

    @router.get("/", response_model=Page[UserSchema])
    async def get_users(
        pagination: PaginationParams = Depends(),
        role: UserRole = None,
        search: str = None,
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


__all__ = ["setup_routes"]

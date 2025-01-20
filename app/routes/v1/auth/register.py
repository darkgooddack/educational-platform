"""
Роутер регистрации пользователей.

Предоставляет эндпоинты для регистрации новых пользователей.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session
from app.schemas import RegistrationSchema, RegistrationResponseSchema
from app.services import UserService

def setup_routes(router: APIRouter):
    """
    Настройка маршрутов для регистрации пользователей.

    Args:
        router (APIRouter): Роутер FastAPI

    Routes:
        POST /register: Регистрация нового пользователя
    """
    @router.post("/")
    async def registration_user(
        user: RegistrationSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> RegistrationResponseSchema:
        """
        📝 **Регистрирует нового пользователя.**

        **Args**:
        - **user_data**: Данные нового пользователя

        **Returns**:
        - **RegistrationResponseSchema**: Схема ответа при успешной регистрации
        """

        return await UserService(db_session).create_user(user)

__all__ = ["setup_routes"]
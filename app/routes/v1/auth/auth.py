"""
Роутер аутентификации пользователей.

Этот модуль содержит роутеры:
- Аутентификации пользователей
- Выхода из системы
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, oauth2_schema
from app.schemas import AuthSchema, TokenResponseSchema
from app.services import AuthService


def setup_routes(router: APIRouter):
    """
    Настройка маршрутов для аутентификации.

    Args:
        router (APIRouter): Роутер FastAPI

    Routes:
        - POST /auth:
            Аутентификация пользователя по email и возвращает JWT токен
        - POST /logout:
            Выход из системы
    """

    @router.post("")
    async def authenticate(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TokenResponseSchema:
        """
        🔐 **Аутентифицирует пользователя по username(email) и возвращает JWT токен.**

        **Args**:
        - **form_data**: Данные для аутентификации username и password (OAuth2PasswordRequestForm)

        **Returns**:
        - **TokenResponseSchema**: Токен доступа с access_token и token_type
        """
        return await AuthService(db_session).authenticate(
            AuthSchema(email=form_data.username, password=form_data.password)
        )

    @router.post("/logout")
    async def logout(
        token: str = Depends(oauth2_schema),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> dict:
        """
        👋 **Выход пользователя из системы.**

        **Args**:
        - **token**: Токен доступа для выхода
        - **redis**: Redis клиент для удаления токена из кэша

        **Returns**:
        - **dict**: {"message": "Выход выполнен успешно!"}
        """
        return await AuthService(db_session).logout(token)


__all__ = ["setup_routes"]

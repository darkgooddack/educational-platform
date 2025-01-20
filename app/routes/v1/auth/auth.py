"""
Роутер аутентификации пользователей.

Этот модуль содержит роутеры:
- Аутентификации пользователей
- Выхода из системы
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, oauth2_schema
from app.schemas import AuthSchema, TokenSchema
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
        credentials: AuthSchema,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> TokenSchema:
        """
        🔐 **Аутентифицирует пользователя по email и возвращает JWT токен.**

        **Args**:
        - **credentials**: Данные для аутентификации (AuthSchema)

        **Returns**:
        - **TokenSchema**: Токен доступа с access_token и token_type

        **Raises**:
        - **UserNotFoundError**: Если пользователь не найден
        """
        return await AuthService(db_session).authenticate(credentials)



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
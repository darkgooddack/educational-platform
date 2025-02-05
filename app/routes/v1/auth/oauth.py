"""
Роутер аутентификации пользователей.

Этот модуль содержит роутеры:
- Аутентификации пользователей через OAuth2.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.schemas import OAuthResponse
from app.services import OAuthService


def setup_routes(router: APIRouter):
    """
    Настройка маршрутов для OAuth2 аутентификации.

    Args:
        router (APIRouter): Роутер FastAPI

    Routes:
        GET /{provider}:
            Редирект на страницу авторизации провайдера.
        GET /{provider}/callback:
            Обработка callback запроса от провайдера.
    """

    @router.get("/{provider}", response_class=RedirectResponse)
    async def oauth(
        provider: str,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> RedirectResponse:
        """
        🌐 **Редирект на страницу авторизации провайдера.**

        **Args**:
        - **provider**: Имя провайдера (vk/google/yandex)

        **Returns**:
        - **RedirectResponse**: Редирект на страницу авторизации
        """
        return await OAuthService(db_session).get_oauth_url(provider)

    @router.get("/{provider}/callback")
    async def oauth_callback(
        provider: str,
        code: str,
        state: str = None,
        device_id: str | None = None,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> OAuthResponse:
        """
        🔄 **Обработка ответа от OAuth провайдера.**

        **Args**:
        - **provider**: Имя провайдера
        - **code**: Код авторизации от провайдера

        **Returns**:
        - **OAuthResponse**: Токен доступа
        """
        return await OAuthService(db_session).authenticate(provider, code, state, device_id)


__all__ = ["setup_routes"]

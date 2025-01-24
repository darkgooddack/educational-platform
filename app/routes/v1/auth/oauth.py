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

        **Raises**:
        - **HTTPException**: Если провайдер не поддерживается
        """
        return await OAuthService(db_session).get_oauth_url(provider)

    @router.get("/{provider}/callback", response_class=RedirectResponse)
    async def oauth_callback(
        provider: str,
        code: str,
        redirect_uri: str
        db_session: AsyncSession = Depends(get_db_session),
    ) -> RedirectResponse:
        """
        🔄 **Обработка ответа от OAuth провайдера.**

        **Args**:
        - **provider**: Имя провайдера
        - **code**: Код авторизации от провайдера
        - **redirect_uri**: URL для редиректа после авторизации
        **Returns**: 
        - **OAuthResponse**: Токен доступа
        """
        auth_result = await OAuthService(db_session).oauthenticate(
            provider=provider,
            code=code,
            redirect_uri=redirect_uri
        )
    
        return RedirectResponse(f"{redirect_uri}?token={auth_result.access_token}")


__all__ = ["setup_routes"]

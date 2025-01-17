"""
Модуль для настройки маршрутов API.
"""
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

def setup_routes(router: APIRouter):
    """
    Настройка маршрутов для API.

    Args:
        router (APIRouter): Объект APIRouter.
    
    Routes:
        GET /: Перенаправление на документацию
    """
    @router.get("/")
    async def root():
        """
        Перенаправление на документацию
        """
        return RedirectResponse(url="/docs")
"""
Модуль для объединения всех роутеров API v1.

BASE_MODULES - без префикса api/v1:
- health (здоровье)

API_MODULES - с префиксом api/v1:
- authentication (аутентификация)
- registration (регистрация)

"""

from fastapi import APIRouter
from app.core.config import config
from .auth import auth_router, oauth_router, register_router

from . import health
router_health = APIRouter(**config.SERVICES["health"].to_dict())
health.setup_routes(router_health)
health_router = router_health

BASE_MODULES = {
    "health": health_router,
}

VERSIONS_MODULES = {
    "auth": auth_router,
    "oauth": oauth_router,
    "register": register_router,
}


def _include_modules(modules: dict) -> APIRouter:
    """
    Хелпер для подключения модулей

    Args:
        modules: dict - словарь с модулями

    Returns:
        APIRouter - роутер
    """
    router = APIRouter()
    for module in modules.values():
        router.include_router(module)
    return router


def get_base_routes() -> APIRouter:
    """
    Возвращает роутеры для базовых модулей

    Returns:
        APIRouter - роутер
    """
    return _include_modules(BASE_MODULES)


def get_api_routes() -> APIRouter:
    """
    Возвращает роутеры для API модулей

    Returns:
        APIRouter - роутер
    """
    return _include_modules(VERSIONS_MODULES)

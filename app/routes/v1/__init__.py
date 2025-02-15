"""
Модуль для объединения всех роутеров API v1.

BASE_MODULES - без префикса api/v1:
- main (главная страница)

API_MODULES - с префиксом api/v1:
- auth (аутентификация)
- register (регистрация)
- oauth (OAuth)
- feedbacks (отзывы)

"""

from fastapi import APIRouter

from app.core.config import config

from . import main
from .auth import auth_router, oauth_router, register_router
from .feedbacks import feedbacks_router
from .users import users_router

router_main = APIRouter(**config.SERVICES["main"].to_dict())
main.setup_routes(router_main)
main_router = router_main

BASE_MODULES = {
    "main": router_main,
}

VERSIONS_MODULES = { # Здесь же порядок отображения в Swagger
    "auth": auth_router,
    "oauth": oauth_router,
    "register": register_router,
    "users": users_router,
    "feedbacks": feedbacks_router,
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

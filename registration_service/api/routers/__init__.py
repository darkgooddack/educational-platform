"""
Модуль для объединения всех роутеров приложения.

Поддерживаемые версии API:
- v1 (текущая версия)
- v2 (в перспективе)
"""

from fastapi import APIRouter
from api.core.config import app_config
from api.routers import v1  # , v2  # будет добавлено позже

VERSIONS_MAP = BASE_ROUTERS = {
    "v1": v1,
    # "v2": v2  # будет добавлено позже
}


def all_routers() -> APIRouter:
    """
    Возвращает основной роутер со всеми подключенными эндпоинтами

    Returns:
        APIRouter: основной роутер
    """
    router = APIRouter()

    # Подключаем базовые роуты без версионного префикса
    for module in BASE_ROUTERS.values():
        router.include_router(module.get_base_routers())

    # Подключаем версионированные API роуты
    for version in app_config.API_VERSIONS:
        if version in VERSIONS_MAP:
            version_router = VERSIONS_MAP[version].get_api_routers()
            router.include_router(router=version_router, prefix=f"/api/{version}")

    return router

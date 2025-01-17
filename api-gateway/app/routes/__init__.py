"""
Модуль для объединения всех роутеров приложения.

Поддерживаемые версии API:
- v1 (текущая версия)
- v2 (в перспективе)
"""

from fastapi import APIRouter

from app.core.config import config
from app.routes import v1  # , v2  # будет добавлено позже

VERSIONS_MAP = {
    "v1": v1,
    # "v2": v2  # будет добавлено позже
}


def all_routes() -> APIRouter:
    """
    Возвращает основной роутер со всеми подключенными эндпоинтами

    Returns:
        APIRouter: основной роутер
    """
    router = APIRouter()

    # Базовые роуты
    for module in VERSIONS_MAP.values():
        router.include_router(module.get_base_routes())

    # Версионированные API роуты
    for version in config.API_VERSIONS:
        if version in VERSIONS_MAP:
            version_router = VERSIONS_MAP[version].get_api_routes()
            router.include_router(router=version_router, prefix=f"/api/{version}")

    return router

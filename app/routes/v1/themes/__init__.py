from fastapi import APIRouter

from app.core.config import config

from . import themes

# Создаем роутеры из конфига
router_themes = APIRouter(**config.SERVICES["themes"].to_dict())


# Подключаем эндпоинты
themes.setup_routes(router_themes)


# Экспортируем роутеры для v1/__init__.py
themes_router = router_themes

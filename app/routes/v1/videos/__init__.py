from fastapi import APIRouter

from app.core.config import config

from . import videos

# Создаем роутеры из конфига
router_videos = APIRouter(**config.SERVICES["videos"].to_dict())


# Подключаем эндпоинты
videos.setup_routes(router_videos)


# Экспортируем роутеры для v1/__init__.py
videos_router = router_videos

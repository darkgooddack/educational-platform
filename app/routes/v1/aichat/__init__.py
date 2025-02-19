from fastapi import APIRouter

from app.core.config import config

from . import aichat

# Создаем роутеры из конфига
router_aichat = APIRouter(**config.SERVICES["aichat"].to_dict())


# Подключаем эндпоинты
aichat.setup_routes(router_aichat)


# Экспортируем роутеры для v1/__init__.py
aichat_router = router_aichat

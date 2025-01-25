from fastapi import APIRouter

from app.core.config import config

from . import feedbacks

# Создаем роутеры из конфига
router_feedbacks = APIRouter(**config.SERVICES["feedbacks"].to_dict())


# Подключаем эндпоинты
feedbacks.setup_routes(router_feedbacks)


# Экспортируем роутеры для v1/__init__.py
feedbacks_router = router_feedbacks

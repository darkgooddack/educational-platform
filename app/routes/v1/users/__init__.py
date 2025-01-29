from fastapi import APIRouter

from app.core.config import config

from . import users

# Создаем роутеры из конфига
router_users = APIRouter(**config.SERVICES["users"].to_dict())


# Подключаем эндпоинты
users.setup_routes(router_users)


# Экспортируем роутеры для v1/__init__.py
users_router = router_users

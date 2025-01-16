from fastapi import APIRouter

from app.core.config import config

from . import auth, oauth, register

# Создаем роутеры из конфига
router_auth = APIRouter(**config.SERVICES["auth"].to_dict())
router_oauth = APIRouter(**config.SERVICES["oauth"].to_dict())
router_register = APIRouter(**config.SERVICES["register"].to_dict())

# Подключаем эндпоинты
auth.setup_routes(router_auth)
oauth.setup_routes(router_oauth)
register.setup_routes(router_register)

# Экспортируем роутеры для v1/__init__.py
auth_router = router_auth
oauth_router = router_oauth
register_router = router_register

from fastapi import APIRouter

from app.core.config import config

from . import tests

# Создаем роутеры из конфига
router_tests = APIRouter(**config.SERVICES["tests"].to_dict())


# Подключаем эндпоинты
tests.setup_routes(router_tests)


# Экспортируем роутеры для v1/__init__.py
tests_router = router_tests

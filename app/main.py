"""
Главный модуль приложения.

Инициализирует FastAPI приложение с:
- Подключением всех роутов
- Настройкой CORS
- Middleware для логирования
- Защитой документации
- Параметрами запуска uvicorn
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import config
from app.core.logging import setup_logging
from app.core.middlewares.docs_auth import DocsAuthMiddleware
from app.core.middlewares.logging import LoggingMiddleware
from app.routes import all_routes
from app.core.handlers import api_exception_handler
from app.core.exceptions import BaseAPIException

# Создаем FastAPI приложение с параметрами из конфига
app = FastAPI(**config.app_params)
setup_logging()

# Добавляем обработчик исключений
app.add_exception_handler(BaseAPIException, api_exception_handler)

# Добавляем middleware в порядке выполнения
app.add_middleware(LoggingMiddleware)  # Логирование запросов
app.add_middleware(DocsAuthMiddleware)  # Защита документации
app.add_middleware(CORSMiddleware, **config.cors_params)  # CORS политики

# Подключаем все маршруты
app.include_router(all_routes())

# Запуск через uvicorn при прямом вызове файла
if __name__ == "__main__":
    uvicorn.run(app, **config.uvicorn_params)

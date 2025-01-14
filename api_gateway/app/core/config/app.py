"""
Модуль основной конфигурации приложения.

Содержит настройки FastAPI приложения, логирования и параметры запуска сервера.
"""

from pathlib import Path
from typing import Any, Dict, List

from pydantic import Field

from app.core.lifespan import lifespan


class ServiceConfig:
    """
    Конфигурация сервисных эндпоинтов.

    Attributes:
        prefix (str): Префикс URL для группы эндпоинтов
        tags (List[str]): Список тегов для Swagger документации

    Example:
        >>> service = ServiceConfig("users", ["Users API"])
        >>> service.to_dict()
        {'prefix': '/users', 'tags': ['Users API']}
    """

    def __init__(self, prefix: str, tags: List[str]):
        """
        Args:
            prefix: Префикс URL без начального слеша
            tags: Список тегов для группировки эндпоинтов
        """
        self.prefix = f"/{prefix}" if prefix else ""
        self.tags = tags

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует конфигурацию в словарь для FastAPI router.

        Returns:
            Dict с prefix и tags для настройки APIRouter
        """
        return {"prefix": self.prefix, "tags": self.tags}


class PathConfig:
    """
    Конфигурация путей проекта.

    Attributes:
        ENV_FILE (Path): Путь к файлу переменных окружения
        APP_DIR (Path): Путь к директории приложения
        BASE_PATH (Path): Корневой путь проекта
        ENV_PATH (Path): Полный путь к .env файлу
        APP_PATH (Path): Полный путь к директории приложения
    """

    ENV_FILE = Path(".env")
    APP_DIR = Path("app")

    BASE_PATH = Path(__file__).resolve().parents[2]  #! проверить
    ENV_PATH = BASE_PATH / ENV_FILE
    APP_PATH = BASE_PATH / APP_DIR


class AppConfig:
    """
    Основная конфигурация приложения.
    """

    logging_level: str = "DEBUG"
    logging_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    TITLE: str = "Educational Platform API Gateway"
    DESCRIPTION: str = "API Gateway для образовательной платформы"
    VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    API_VERSIONS = ["v1"]  # Поддерживаемые версии API

    SERVICES = {
        "health": ServiceConfig("health", ["Health"]),
        "authentication": ServiceConfig("authenticate", ["Authentication"]),
        "registration": ServiceConfig("registration", ["Registration"]),
    }

    PATHS = PathConfig()

    app_url: str = "https://api.ebtest.ru"

    redis_pool_size: int = Field(
        default=10, description="Размер пула подключений к Redis"
    )

    rabbitmq_connection_timeout: int = Field(
        default=30, description="Таймаут подключения к RabbitMQ"
    )
    rabbitmq_exchange: str = Field(
        default="educational_platform", description="Название exchange в RabbitMQ"
    )

    @property
    def app_params(self) -> dict:
        return {
            "title": self.TITLE,
            "description": self.DESCRIPTION,
            "version": self.VERSION,
            "swagger_ui_parameters": {"defaultModelsExpandDepth": -1},
            "root_path": "",
            "lifespan": lifespan,
        }

    @property
    def uvicorn_params(self) -> dict:
        return {
            "host": self.HOST,
            "port": self.PORT,
            "proxy_headers": True,
        }


app_config = AppConfig()

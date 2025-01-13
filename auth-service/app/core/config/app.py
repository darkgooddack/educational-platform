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

    Attributes:
        logging_level (str): Уровень логирования
        logging_format (str): Формат сообщений лога
        TITLE (str): Название сервиса
        DESCRIPTION (str): Описание сервиса
        VERSION (str): Версия API
        HOST (str): Хост для запуска сервера
        PORT (int): Порт для запуска сервера
        API_VERSIONS (List[str]): Поддерживаемые версии API
        SERVICES (Dict): Конфигурация эндпоинтов
        PATHS (PathConfig): Конфигурация путей
        auth_url (str): URL для аутентификации
        redis_url (str): URL для Redis
        app_params (Dict): Параметры запуска FastAPI
        lifespan (Callable): Функция жизненного цикла приложения


    Example:
        >>> from app.core.config import config
        >>> config.app_params
        {'title': 'Auth microoservice', 'description': ... }
    """

    logging_level: str = "DEBUG"
    logging_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    TITLE: str = "Auth microoservice"
    DESCRIPTION: str = (
        "Service of authentication and registration for educational platform"
    )
    VERSION: str = "0.1.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    API_VERSIONS = ["v1"]  # Поддерживаемые версии API

    SERVICES = {
        "health": ServiceConfig("health", ["Health"]),
        "authentication": ServiceConfig("authenticate", ["Authentication"]),
        "registration": ServiceConfig("registration", ["Registration"]),
    }

    PATHS = PathConfig()

    auth_url: str = Field(
        default="api/v1/authenticate", description="URL для аутентификации пользователя"
    )

    token_type: str = Field(default="bearer", description="Тип токена авторизации")

    token_algorithm: str = Field(
        default="HS256", description="Алгоритм шифрования JWT токена"
    )

    token_expire_minutes: int = Field(
        default=1440, description="Время жизни токена в минутах"
    )

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
        """
        Параметры для инициализации FastAPI приложения.

        Returns:
            Dict с настройками FastAPI
        """
        return {
            "title": self.TITLE,
            "description": self.DESCRIPTION,
            "version": self.VERSION,
            "swagger_ui_parameters": {
                "defaultModelsExpandDepth": -1
            },  # Сворачивание моделей в Swagger UI
            "root_path": "",  # Пустой путь для корневого маршрута
            "lifespan": lifespan,
        }

    @property
    def uvicorn_params(self) -> dict:
        """
        Параметры для запуска uvicorn сервера.

        Returns:
            Dict с настройками uvicorn
        """
        return {
            "host": self.HOST,
            "port": self.PORT,
            "proxy_headers": True,  # Для корректной работы с прокси-серверами
        }


app_config = AppConfig()

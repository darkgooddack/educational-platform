from typing import Dict, List, Any
from pathlib import Path
from app.core.redis.lifespan import lifespan


class ServiceConfig:
    """
    Конфигурация сервиса регистрации пользователей.
    """

    def __init__(self, prefix: str, tags: List[str]):
        self.prefix = f"/{prefix}" if prefix else ""
        self.tags = tags

    def to_dict(self) -> Dict[str, Any]:
        """
        Возвращает словарь с параметрами конфигурации сервиса.
        """
        return {"prefix": self.prefix, "tags": self.tags}


class PathConfig:
    """
    Конфигурация путей сервиса регистрации пользователей.
    """

    ENV_FILE = Path(".env")
    APP_DIR = Path("app")

    BASE_PATH = Path(__file__).resolve().parents[4] # /microservice/app/core/config
    ENV_PATH = BASE_PATH / ENV_FILE
    APP_PATH = BASE_PATH / APP_DIR


class AppConfig:
    """
    Конфигурация микросервиса регистрации пользователей.
    """

    TITLE: str = "Registration Service"
    DESCRIPTION: str = "Registration service for educational platform"
    VERSION: str = "0.1.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    API_VERSIONS = ["v1"]  # Поддерживаемые версии API

    SERVICES = {
        "registration": ServiceConfig("registration", ["Registration"]),
        "oauth": ServiceConfig("oauth", ["OAuth"]),
        "verification": ServiceConfig("verification", ["Verification"]),
    }

    PATHS = PathConfig()

    @property
    def app_params(self) -> dict:
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
        return {
            "host": self.HOST,
            "port": self.PORT,
            "proxy_headers": True,  # Для корректной работы с прокси-серверами
        }

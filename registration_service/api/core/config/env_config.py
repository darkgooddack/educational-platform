from typing import Dict, List, Any
from pydantic import Field, SecretStr, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from .app_config import AppConfig


class Settings(BaseSettings):

    logging_level: str = "DEBUG"
    logging_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    dsn: str = Field(default="sqlite+aiosqlite:///./test.db") #! TODO: поменять, по умолчанию для локальных тестов
    docs_access: bool = True

    allow_origins: List[str] = Field(default_factory=list)
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]

    @property
    def cors_params(self) -> Dict[str, Any]:
        return {
            "allow_origins": self.allow_origins,
            "allow_credentials": self.allow_credentials,
            "allow_methods": self.allow_methods,
            "allow_headers": self.allow_headers,
        }

    model_config = SettingsConfigDict(
        env_file=AppConfig.PATHS.ENV_PATH,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # Разделитель вложенных переменных окружения
        extra="allow",  # Разрешить дополнительные параметры
    )
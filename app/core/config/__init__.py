"""
Пакет конфигурации приложения.

Предоставляет централизованный доступ к настройкам всего приложения
через единый объект config.

Example:
    >>> from app.core.config import config
    >>> config.database_dsn
    'sqlite+aiosqlite:///./test.db'
    >>> config.docs_access
    True
    >>> config.TITLE
    'Registration Service'

    Или:
    >>> import app.core.config as config
    >>> config.PORT
    8001
"""

import logging
from functools import lru_cache

from .app import AppConfig, LogConfig
from .settings import Settings

logger = logging.getLogger(__name__)


class Config(Settings, AppConfig):
    """
    Объединенная конфигурация приложения.
    Наследует все настройки из Settings и AppConfig.
    """

    def __init__(self, **kwargs):
        Settings.__init__(self, **kwargs)
        AppConfig.__init__(self)
        self.LOGGING = LogConfig(self)
        print("\n⚙️  Параметры конфигурации:")
        print(f"🔌 DATABASE_DSN: {self.database_dsn}")
        print(f"🔗 REDIS_URL: {self.redis_url}")
        print(f"🐰 RABBITMQ_DSN: {self.rabbitmq_dsn}")
        print(f"📦 AWS S3: {self.aws_endpoint}")


@lru_cache
def get_config() -> Config:
    """
    Получение конфигурации приложения из кэша.
    """
    config_instance = Config()

    return config_instance


# def clear_config_cache():
# get_config.cache_clear()
# return get_config()

# config = clear_config_cache()

config = get_config()

logger.info(f"Config loaded: {config}")
__all__ = ["config"]

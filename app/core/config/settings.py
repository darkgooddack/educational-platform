"""
Модуль настроек из переменных окружения.

Обеспечивает:
- Загрузку конфигурации из .env файла
- Настройку подключений к сервисам (Redis, RabbitMQ, DB)
- Конфигурацию CORS политик
- Управление доступом к документации API
"""
import logging
import secrets
from typing import Any, Dict, List

from pydantic import AmqpDsn, Field, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .app import AppConfig

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Конфигурация параметров приложения из переменных окружения.

    Attributes:
        docs_username (str): Имя пользователя для доступа к docs/redoc
        docs_password (str): Пароль для доступа к docs/redoc
        token_key (SecretStr): Секретный ключ для JWT токенов
        redis_url (RedisDsn): URL подключения к Redis
        database_dsn (str): URL подключения к базе данных
        rabbitmq_dsn (AmqpDsn): URL подключения к RabbitMQ
        allow_origins (List[str]): Разрешенные источники для CORS
        allow_credentials (bool): Разрешение передачи учетных данных для CORS
        allow_methods (List[str]): Разрешенные HTTP методы для CORS
        allow_headers (List[str]): Разрешенные HTTP заголовки для CORS

    Properties:
        rabbitmq_params: Параметры подключения к RabbitMQ
        cors_params: Параметры CORS для FastAPI

    Example:
        >>> from app.core.config import config
        >>> print(config.database_dsn)
        "sqlite+aiosqlite:///./test.db"
        >>> print(config.cors_params)
        {
            'allow_origins': [],
            'allow_credentials': True,
            'allow_methods': ['*'],
            'allow_headers': ['*']
        }
    """

    docs_access: bool = Field(
        default=True, description="Разрешение доступа к документации API"
    )

    docs_username: str = Field(
        default="admin", description="Имя пользователя для доступа к docs/redoc"
    )

    docs_password: str = Field(
        default="admin", description="Паспорт для доступа к docs/redoc"
    )

    token_key: SecretStr = Field(
        default=SecretStr(secrets.token_hex(32)),
        description="Секретный ключ для токена",
    )

    redis_url: RedisDsn = Field(
        default="redis://default:default@redis:6379",
        description="Ссылка для подключения к Redis",
    )

    database_dsn: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/educational_db",
        description="Ссылка для подключения к базе данных",
    )

    rabbitmq_dsn: AmqpDsn = Field(
        default="amqp://guest:guest@rabbitmq:5672/",
        description="URL подключения к RabbitMQ",
    )

    allow_origins: List[str] = Field(
        default_factory=list, description="Список разрешенных origins для CORS"
    )
    allow_credentials: bool = Field(
        default=True, description="Allow credentials для CORS"
    )
    allow_methods: List[str] = Field(
        default=["*"], description="Разрешенные HTTP methods для CORS"
    )
    allow_headers: List[str] = Field(
        default=["*"], description="Разрешенные headers для CORS"
    )

    oauth_providers: Dict[str, Dict[str, str]] = Field(
        default={
            "yandex": {
                "client_id": "",
                "client_secret": "",
                "auth_url": "https://oauth.yandex.ru/authorize",
                "token_url": "https://oauth.yandex.ru/token",
                "user_info_url": "https://login.yandex.ru/info",
                "scope": "login:email",
            },
            "vk": {
                "client_id": "",
                "client_secret": "",
                "auth_url": "https://oauth.vk.com/authorize",
                "token_url": "https://oauth.vk.com/access_token",
                "user_info_url": "https://api.vk.com/method/users.get",
                "scope": "email",
            },
            "google": {
                "client_id": "",
                "client_secret": "",
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scope": "email profile",
            },
        }
    )

    @property
    def rabbitmq_params(self) -> Dict[str, Any]:
        """
        Формирует параметры подключения к RabbitMQ.

        Returns:
            Dict с параметрами подключения к RabbitMQ
        """
        return {
            "url": str(self.rabbitmq_dsn),
            "connection_timeout": AppConfig.rabbitmq_connection_timeout,
            "exchange": AppConfig.rabbitmq_exchange,
        }

    @property
    def cors_params(self) -> Dict[str, Any]:
        """
        Формирует параметры CORS для FastAPI.

        Returns:
            Dict с настройками CORS middleware
        """
        return {
            "allow_origins": self.allow_origins,
            "allow_credentials": self.allow_credentials,
            "allow_methods": self.allow_methods,
            "allow_headers": self.allow_headers,
        }

    model_config = SettingsConfigDict(
        env_file=AppConfig.PATHS.ENV_PATH,
        env_file_encoding="utf-8",
        # env_prefix="EDU__",
        # env_nested_delimiter="__",
        extra="allow",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.info("Loaded configuration:")
        logger.info(f"Database DSN: {self.database_dsn}")
        logger.info(f"Redis URL: {self.redis_url}")
        logger.info(f"RabbitMQ DSN: {self.rabbitmq_dsn}")
        logger.info(f"CORS params: {self.cors_params}")
        logger.info(f"OAuth providers: {self.oauth_providers}")

    def print_config(self):
        print("\nCurrent configuration:")
        print(f"Database DSN: {self.database_dsn}")
        print(f"Redis URL: {self.redis_url}")
        print(f"RabbitMQ DSN: {self.rabbitmq_dsn}")
        print(f"CORS params: {self.cors_params}")
        print(f"OAuth providers: {self.oauth_providers}\n")

c = Settings()
c.print_config()
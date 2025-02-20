"""
Модуль настроек из переменных окружения.

Обеспечивает:
- Загрузку конфигурации из .env файла
- Настройку подключений к сервисам (Redis, RabbitMQ, DB)
- Конфигурацию CORS политик
- Управление доступом к документации API
"""

import logging
import os
import secrets
from typing import Any, ClassVar, Dict, List

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

    app_env: str = Field(default="dev", description="Окружение приложения")

    smtp_server: str = Field("mail.ebtest.ru", description="SMTP сервер")
    smtp_port: int = Field(587, description="SMTP порт")
    sender_email: str = Field("noreply@ebtest.ru", description="Email отправителя")
    smtp_password: SecretStr

    pre_instruction: str = "Ты умный ассистент, который помогает пользователям"

    yandex_model_name: str = Field(
        default="yandexgpt-lite", description="Название модели Yandex GPT"
    )

    yandex_api_url: str = Field(
        default="https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        description="URL API Yandex GPT",
    )
    # Ключ доступа к API Yandex GPT
    yandex_api_key: SecretStr

    yandex_private_key: SecretStr

    yandex_key_id: str

    yandex_folder_id: str = Field(description="ID каталога в Yandex Cloud")

    yandex_max_tokens: int = Field(
        default=2000, description="Максимальное количество токенов"
    )

    yandex_temperature: float = Field(default=0.6, description="Температура генерации")

    @property
    def yandex_model_uri(self) -> str:
        """
        Формирует URI модели Yandex GPT.

        Returns:
            str: URI в формате gpt://{folder_id}/{model_name}
        """
        return f"gpt://{self.yandex_folder_id}/{self.yandex_model_name}"

    log_format: str = Field(default="pretty", description="Формат логов (pretty/json)")

    log_file: str = Field(
        default="./logs/app.log" if os.name == "nt" else "/var/log/app.log",
        description="Путь к файлу логов",
    )

    aws_service_name: str = Field(default="s3", description="Сервис AWS")

    aws_region: str = Field(default="ru-central1", description="Регион AWS")

    aws_endpoint: str

    aws_bucket_name: str = Field(
        default="education-platform", description="Имя бакета AWS"
    )

    aws_access_key_id: str

    aws_secret_access_key: str

    docs_access: bool = Field(
        default=True, description="Разрешение доступа к документации API"
    )

    docs_username: str = Field(
        default="admin", description="Имя пользователя для доступа к docs/redoc"
    )

    docs_password: str = Field(
        default="admin", description="Паспорт для доступа к docs/redoc"
    )

    token_key: SecretStr = secrets.token_hex(32)

    redis_url: RedisDsn = Field(
        default="redis://default:default@localhost:6379",
        description="Ссылка для подключения к Redis",
    )

    database_dsn: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/educational_db",
        description="Ссылка для подключения к базе данных",
    )

    rabbitmq_host: ClassVar[str] = "localhost"
    rabbitmq_dsn: AmqpDsn = Field(
        default=f"amqp://guest:guest@{rabbitmq_host}:5672/",
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
    oauth_callback_base_url: str = Field(
        default="http://localhost:8000/api/v1/oauth/{provider}/callback",
        description="Base URL for OAuth callbacks",
    )
    oauth_providers: Dict[str, Dict[str, str | int]] = Field(
        default={
            "yandex": {
                "client_id": "",
                "client_secret": "",
                "auth_url": "https://oauth.yandex.ru/authorize",
                "token_url": "https://oauth.yandex.ru/token",
                "user_info_url": "https://login.yandex.ru/info",
                "scope": "login:email",
                "callback_url": "http://localhost:8000/api/v1/oauth/yandex/callback",
            },
            "vk": {
                "client_id": 0,  # VK: client_id == id приложения >_<
                "client_secret": "",
                "auth_url": "https://id.vk.com/authorize",
                "token_url": "https://id.vk.com/oauth2/auth",
                "user_info_url": "https://id.vk.com/oauth2/user_info",
                "scope": "email",
                "callback_url": "http://localhost:8000/api/v1/oauth/vk/callback",
            },
            "google": {
                "client_id": "",
                "client_secret": "",
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scope": "email profile",
                "callback_url": "http://localhost:8000/api/v1/oauth/google/callback",
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
    def s3_config_info(self) -> Dict[str, Any]:
        """
        Формирует информацию о конфигурации S3.
        """
        return {
            "aws_service_name": self.aws_service_name,
            "aws_region": self.aws_region,
            "aws_endpoint": self.aws_endpoint,
            "aws_bucket_name": self.aws_bucket_name,
            "aws_access_key_id": self.aws_access_key_id,
            "aws_secret_access_key": self.aws_secret_access_key,
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
        env_nested_delimiter="__",
        extra="allow",
    )

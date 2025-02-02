import pytest
from app.core.config import Settings, AppConfig


@pytest.fixture
def test_settings():
    # Теперь Settings автоматически использует ENV_FILE из окружения
    return Settings()

def test_settings_default_values(test_settings):
    """Проверяет значения по умолчанию в настройках"""
    assert test_settings.aws_service_name == "s3"
    assert test_settings.aws_endpoint == "https://test.storage.com"
    assert test_settings.aws_access_key_id == "test_key_id"
    assert test_settings.aws_secret_access_key == "test_secret_key"
    assert test_settings.docs_access is True
    assert test_settings.docs_username == "test_admin"
    assert test_settings.docs_password == "test_pass"

def test_rabbitmq_params(test_settings):
    """Проверяет формирование параметров RabbitMQ"""
    params = test_settings.rabbitmq_params
    assert params["connection_timeout"] == AppConfig.rabbitmq_connection_timeout
    assert params["exchange"] == AppConfig.rabbitmq_exchange

def test_cors_params(test_settings):
    """Проверяет формирование CORS параметров"""
    params = test_settings.cors_params
    assert params["allow_credentials"] is True
    assert params["allow_methods"] == ["*"]
    assert params["allow_headers"] == ["*"]

def test_oauth_providers(test_settings):
    """Проверяет настройки OAuth провайдеров"""
    yandex = test_settings.oauth_providers["yandex"]
    assert yandex["client_id"] == "test_yandex_id"
    assert yandex["client_secret"] == "test_yandex_secret"

    vk = test_settings.oauth_providers["vk"]
    assert vk["client_id"] == "test_vk_id"
    assert vk["client_secret"] == "test_vk_secret"

    google = test_settings.oauth_providers["google"]
    assert google["client_id"] == "test_google_id"
    assert google["client_secret"] == "test_google_secret"

def test_database_connections(test_settings):
    """Проверяет настройки подключений к базам данных"""
    assert str(test_settings.redis_url) == "redis://test:test@localhost:6380"
    assert test_settings.database_dsn == "postgresql+asyncpg://test:test@localhost:5434/test_db"
    assert str(test_settings.rabbitmq_dsn) == "amqp://test:test@localhost:5672/"

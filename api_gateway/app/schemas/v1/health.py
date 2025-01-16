"""
Модуль содержит схемы для проверки здоровья сервисов.
"""

from enum import Enum


class HealthStatus(Enum):
    """
    Статусы здоровья сервисов.
    - HEALTHY: Все сервисы здоровы
    - TIMEOUT: Таймаут при ожидании ответа от сервиса
    - CONNECTION_ERROR: Ошибка подключения к сервису
    - UNKNOWN_ERROR: Неизвестная ошибка
    """

    HEALTHY = "healthy"
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection"
    UNKNOWN_ERROR = "unknown"


class HealthStatusCodes(Enum):
    """
    Статусы HTTP для ответа на запрос проверки здоровья.
    - OK: Все сервисы здоровы
    - SERVICE_UNAVAILABLE: Один или более сервисов недоступны
    - INTERNAL_ERROR: Внутренняя ошибка сервера
    """

    OK = 204
    SERVICE_UNAVAILABLE = 503
    INTERNAL_ERROR = 500

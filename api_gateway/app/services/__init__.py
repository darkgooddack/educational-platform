"""
Пакет сервисов приложения.

Предоставляет единую точку доступа ко всем сервисам.
"""

from .v1.base import BaseService
from .v1.cache import CacheService

__all__ = [
    "BaseService",
    "CacheService",
]

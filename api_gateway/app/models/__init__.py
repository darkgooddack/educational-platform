"""
Пакет моделей данных.

Предоставляет единую точку доступа ко всем моделям приложения.
"""

from .v1.base import BaseModel
from .v1.cache import TokenCacheModel, RouteCacheModel

__all__ = ["BaseModel", "TokenCacheModel", "RouteCacheModel"]

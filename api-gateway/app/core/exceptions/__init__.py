"""
Пакет исключений приложения.

Предоставляет централизованный доступ ко всем кастомным исключениям.

"""

from .v1.base import BaseAPIException

__all__ = ["BaseAPIException"]

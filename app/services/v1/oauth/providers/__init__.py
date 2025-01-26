"""
Предоставляет единую точку доступа ко всем OAuth провайдерам.
"""

from .google import GoogleOAuthProvider
from .vk import VKOAuthProvider
from .yandex import YandexOAuthProvider

__all__ = [
    "GoogleOAuthProvider",
    "YandexOAuthProvider",
    "VKOAuthProvider",
]

"""
Предоставляет единую точку доступа ко всем OAuth провайдерам.
"""
from .google import GoogleOAuthProvider
from .yandex import YandexOAuthProvider
from .vk import VKOAuthProvider


__all__ = [
    "GoogleOAuthProvider",
    "YandexOAuthProvider",
    "VKOAuthProvider",
]

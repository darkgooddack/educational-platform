import logging

from app.core.config import config


def setup_logging():
    """
    Настройка логгера для всего приложения
    """
    logging.basicConfig(**config.LOGGING.to_dict())

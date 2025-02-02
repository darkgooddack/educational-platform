import logging
from logging.handlers import RotatingFileHandler

from app.core.config import config


def setup_logging():
    """
    Настройка логгера для всего приложения
    """
    # Очищаем существующие хендлеры
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    log_config = config.LOGGING.to_dict()

    # Убираем параметры хендлера из базового конфига
    handler_params = {
        "maxBytes": log_config.pop("maxBytes", None),
        "backupCount": log_config.pop("backupCount", None),
    }

    # Настраиваем базовое логирование
    logging.basicConfig(**log_config)

    # Добавляем консольный хендлер
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(config.LOGGING.FORMAT))
    logging.getLogger().addHandler(console_handler)

    # Добавляем ротирующий файловый хендлер если нужно
    if handler_params["maxBytes"]:
        file_handler = RotatingFileHandler(
            filename=log_config.get("filename"),
            maxBytes=handler_params["maxBytes"],
            backupCount=handler_params["backupCount"],
        )
        file_handler.setFormatter(logging.Formatter(config.LOGGING.FORMAT))
        logging.getLogger().addHandler(file_handler)

    # Настройка логгера для OAuth
    oauth_logger = logging.getLogger("BaseOAuthProvider")
    oauth_logger.setLevel(logging.INFO)
    oauth_logger.addHandler(console_handler)
    oauth_logger.addHandler(file_handler)

    # Филильтрация логов
    logging.getLogger("python_multipart").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)
    logging.getLogger("aio_pika").setLevel(logging.WARNING)
    logging.getLogger("aiormq").setLevel(logging.WARNING)

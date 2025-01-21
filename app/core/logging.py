import logging
from logging.handlers import RotatingFileHandler

from app.core.config import config


def setup_logging():
    """
    Настройка логгера для всего приложения
    """
    log_config = config.LOGGING.to_dict()

    # Убираем параметры хендлера из базового конфига
    handler_params = {
        'maxBytes': log_config.pop('maxBytes', None),
        'backupCount': log_config.pop('backupCount', None)
    }

    # Настраиваем базовое логирование
    logging.basicConfig(**log_config)

    # Добавляем ротирующий файловый хендлер если нужно
    if handler_params['maxBytes']:
        handler = RotatingFileHandler(
            filename=log_config.get('filename'),
            maxBytes=handler_params['maxBytes'],
            backupCount=handler_params['backupCount']
        )
        logging.getLogger().addHandler(handler)

    # Филильтрация логов
    logging.getLogger("aio_pika.robust_connection").setLevel(logging.INFO)
    logging.getLogger("aiormq.connection").setLevel(logging.INFO)
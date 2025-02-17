import os
import logging
from datetime import datetime
import json
from pathlib import Path
from app.core.config import config

class PrettyFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[41m', # Red background
    }
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✨',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '💥',
    }

    RESET = '\033[0m'

    def format(self, record):
        standard_attrs = {'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                     'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                     'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                     'thread', 'threadName', 'processName', 'process', 'message',
                     'asctime'}

        extra_attrs = {k: v for k, v in vars(record).items()
                      if k not in standard_attrs}

        if extra_attrs:
            extra_msg = f"\033[33m[extra: {extra_attrs}]\033[0m"
        else:
            extra_msg = ""

        emoji = self.EMOJIS.get(record.levelname, '')

        base_msg = config.LOGGING.PRETTY_FORMAT % {
            'asctime': self.formatTime(record),
            'name': record.name,
            'levelname': f"{self.COLORS.get(record.levelname, '')}{record.levelname} {self.RESET}",
            'message': f"{emoji} {record.getMessage()}"
        }

        return f"{base_msg} {extra_msg}" if extra_msg else base_msg

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = config.LOGGING.JSON_FORMAT.copy()

        for key, value in log_data.items():
            if key == 'timestamp':
                # Используем datetime для форматирования с микросекундами
                dt = datetime.fromtimestamp(record.created)
                log_data[key] = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            else:
                log_data[key] = value % {
                    'asctime': self.formatTime(record),
                    'levelname': record.levelname,
                    'module': record.module,
                    'funcName': record.funcName,
                    'message': record.getMessage()
                }

        return json.dumps(log_data, ensure_ascii=False)

def setup_logging():
    root = logging.getLogger()

    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)

    log_config = config.LOGGING.to_dict()

    # Консольный хендлер с pretty/json форматом из конфига
    console_formatter = JsonFormatter() if config.LOGGING.LOG_FORMAT == "json" else PrettyFormatter()
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

   # Файловый хендлер всегда с JSON форматом
    if log_config.get("filename"):
        log_path = Path(log_config["filename"])

        # Создаем директорию с нужными правами
        if not log_path.parent.exists():
            os.makedirs(str(log_path.parent), exist_ok=True)

        file_handler = logging.FileHandler(
            filename=log_config["filename"],
            mode=log_config.get("filemode", "a"),
            encoding=log_config.get("encoding", "utf-8")
        )
        file_handler.setFormatter(JsonFormatter())
        root.addHandler(file_handler)

    root.setLevel(log_config.get("level", logging.INFO))

    for logger_name in ["python_multipart", "sqlalchemy.engine", "passlib", "aio_pika", "aiormq"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

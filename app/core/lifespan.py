"""
Модуль жизненного цикла приложения.

Этот модуль содержит функцию жизненного цикла приложения,
которая инициализирует и закрывает подключения к Redis и RabbitMQ.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Жизненный цикл приложения.

    Эта функция вызывается при запуске приложения и завершении работы.
    Она инициализирует и закрывает подключение к Redis и RabbitMQ.

    Args:
        _app: Экземпляр FastAPI приложения.

    """
    from app.core.dependencies.rabbitmq import RabbitMQClient
    from app.core.dependencies.redis import RedisClient

    await RedisClient.get_instance()
    await RabbitMQClient.get_instance()
    if not RabbitMQClient.is_connected():
        logging.warning("RabbitMQ: ошибка подключения!")
    else:
        logging.info("RabbitMQ: подключение успешно!")

    yield

    await RedisClient.close()
    await RabbitMQClient.close()

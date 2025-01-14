"""
Модуль жизненного цикла приложения.

Этот модуль содержит функцию жизненного цикла приложения,
которая инициализирует и закрывает подключения к Redis и RabbitMQ.
"""

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
    from app.core.dependencies import RedisClient, RabbitMQClient
    from app.core.health import setup_health_check



    _redis = await RedisClient.get_instance()
    rabbitmq_client = await RabbitMQClient.get_instance()

    channel = await rabbitmq_client.channel()
    await setup_health_check(_app, channel)

    yield

    await RedisClient.close()
    await RabbitMQClient.close()

"""
Модуль жизненного цикла приложения.

Этот модуль содержит функцию жизненного цикла приложения,
которая инициализирует и закрывает подключения к Redis и RabbitMQ.
"""
import asyncio
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
    from app.core.scheduler import scheduler
    scheduler.start()
    logging.info("Планировщик успешно запущен")

    for attempt in range(RabbitMQClient._max_retries):
        await RedisClient.get_instance()
        await RabbitMQClient.get_instance()

        if await RabbitMQClient.health_check():
            break

        if attempt == RabbitMQClient._max_retries - 1:
            logging.warning("RabbitMQ: ошибка подключения после всех попыток!")
        else:
            logging.info(f"RabbitMQ: попытка подключения {attempt + 1}")
            await asyncio.sleep(RabbitMQClient._retry_delay)


    yield

    await RedisClient.close()
    await RabbitMQClient.close()

    scheduler.shutdown()
    logging.info("Планировщик успешно остановлен")
    
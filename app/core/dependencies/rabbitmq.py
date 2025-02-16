"""
Модуль для подключения к RabbitMQ.
"""
import asyncio
from typing import Optional
from aio_pika import Connection, connect_robust

from app.core.config import config


class RabbitMQClient:
    """
    Клиент для работы с RabbitMQ.

    Реализует паттерн Singleton для поддержания единственного подключения.
    """

    _instance: Optional[Connection] = None
    _is_connected: bool = False
    _max_retries: int = 5
    _retry_delay: int = 5

    @classmethod
    async def get_instance(cls) -> Optional[Connection]:
        """
        Получает единственный экземпляр подключения к RabbitMQ.

        Returns:
            Connection: Активное подключение к RabbitMQ
        """
        if not cls._instance and not cls._is_connected:
            for attempt in range(cls._max_retries):
                try:
                    cls._instance = await connect_robust(**config.rabbitmq_params)
                    cls._is_connected = True
                    break
                except Exception:
                    if attempt < cls._max_retries - 1:
                        await asyncio.sleep(cls._retry_delay)
                    else:
                        cls._is_connected = False
                        cls._instance = None
        return cls._instance

    @classmethod
    async def health_check(cls) -> bool:
        if not cls._instance or not cls._is_connected:
            return False
        try:
            # Проверяем что соединение живо
            return not cls._instance.is_closed
        except Exception:
            return False

    @classmethod
    async def close(cls):
        """
        Закрывает подключение к RabbitMQ.
        """
        if cls._instance and cls._is_connected:
            try:
                await cls._instance.close()
            finally:
                cls._instance = None
                cls._is_connected = False

    @classmethod
    def is_connected(cls) -> bool:
        return cls._is_connected


async def get_rabbitmq() -> Optional[Connection]:
    """
    FastAPI зависимость для получения подключения к RabbitMQ.

    Returns:
        Connection: Активное подключение к RabbitMQ
    """
    connection = await RabbitMQClient.get_instance()
    if connection and await RabbitMQClient.health_check():
        return connection
    return None

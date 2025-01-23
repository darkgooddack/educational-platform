"""
Модуль для подключения к RabbitMQ.
"""
from aio_pika import Connection, connect_robust

from app.core.config import config


class RabbitMQClient:
    """
    Клиент для работы с RabbitMQ.

    Реализует паттерн Singleton для поддержания единственного подключения.
    """

    _instance: Connection = None
    _is_connected: bool = False

    @classmethod
    async def get_instance(cls) -> Connection | None:
        """
        Получает единственный экземпляр подключения к RabbitMQ.

        Returns:
            Connection: Активное подключение к RabbitMQ
        """
        if not cls._instance and not cls._is_connected:
            try:
                cls._instance = await connect_robust(**config.rabbitmq_params)
                cls._is_connected = True
            except Exception as e:
                cls._is_connected = False
                cls._instance = None
        return cls._instance

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
from aio_pika import Connection, connect_robust

from app.core.config import config


class RabbitMQClient:
    """
    Клиент для работы с RabbitMQ.

    Реализует паттерн Singleton для поддержания единственного подключения.
    """

    _instance: Connection = None

    @classmethod
    async def get_instance(cls) -> Connection:
        """
        Получает единственный экземпляр подключения к RabbitMQ.

        Returns:
            Connection: Активное подключение к RabbitMQ
        """
        if not cls._instance:
            cls._instance = await connect_robust(**config.rabbitmq_params)
        return cls._instance

    @classmethod
    async def close(cls):
        """
        Закрывает подключение к RabbitMQ.
        """
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
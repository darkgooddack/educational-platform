"""
Модуль для работы с RabbitMQ.

"""

from app.core.clients import RabbitMQClient


async def get_rabbitmq():
    """
    FastAPI зависимость для получения подключения к RabbitMQ.

    Returns:
        Connection: Активное подключение к RabbitMQ
    """
    connection = await RabbitMQClient.get_instance()
    return connection

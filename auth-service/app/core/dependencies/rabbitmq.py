"""
Модуль для работы с RabbitMQ.

Предоставляет единый интерфейс подключения к RabbitMQ через паттерн Singleton.
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

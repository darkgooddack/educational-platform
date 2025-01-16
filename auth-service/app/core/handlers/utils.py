import json
import logging

from aio_pika import IncomingMessage, Message, RobustConnection, connect_robust

from app.core.config import config

logger = logging.getLogger(__name__)


async def send_response(message: IncomingMessage, status: dict) -> None:
    """
    Отправляет ответ обратно в очередь.

    Args:
        message: Входящее сообщение с reply_to
        status: Статус ответа в формате словаря

    Returns: None
    """
    try:
        logger.debug(
            "📨 Отправляю ответ в очередь %s: %s",
            message.reply_to,
            json.dumps(status, indent=2),
        )

        connection: RobustConnection = await connect_robust(**config.rabbitmq_params)
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                Message(
                    body=json.dumps(status).encode(), content_type="application/json"
                ),
                routing_key=message.reply_to,
            )
        logger.debug("✅ Ответ успешно отправлен")
    except ConnectionError as e:
        logger.error("🔌 Ошибка подключения к RabbitMQ: %s", str(e))
    except TimeoutError as e:
        logger.error("⏰ Таймаут отправки сообщения: %s", str(e))
    except Exception as e:
        logger.error("💀 Ошибка отправки сообщения: %s", str(e))

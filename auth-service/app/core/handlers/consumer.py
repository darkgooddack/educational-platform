"""
Модуль для обработки сообщений из RabbitMQ.

Обрабатывает команды:
- authenticate: аутентификация пользователя
- logout: выход из системы
- health_check: проверка работоспособности
"""

import json
import logging

from aio_pika import IncomingMessage, connect_robust

from app.core.config import config
from app.core.dependencies.database import SessionContextManager
from app.core.handlers import auth, health, oauth, register, utils
from app.services import AuthenticationService, UserService

logger = logging.getLogger(__name__)


async def process_auth_message(
    message: IncomingMessage,
    auth_service: AuthenticationService,
    user_service: UserService,
) -> None:
    """
    Процессинг сообщения из RabbitMQ.

    Args:
        message: Сообщение из RabbitMQ
        auth_service: Сервис аутентификации
        user_service: Сервис пользователей

    Returns: None
    """
    try:
        body = json.loads(message.body.decode())
        action = body.get("action")

        logger.info("📨 Получено сообщение | Action: %s", action)
        logger.debug(
            "📦 Тело запроса: %s", json.dumps(body, indent=2, ensure_ascii=False)
        )

        handlers = {
            "authenticate": lambda: auth.handle_authenticate(
                body.get("data"), auth_service
            ),
            "logout": lambda: auth.handle_logout(
                body.get("data", {}).get("token"), auth_service
            ),
            "oauth_authenticate": lambda: oauth.handle_oauth(
                body["provider"], body["user_data"], auth_service
            ),
            "register": lambda: register.handle_register(body["data"], user_service),
        }

        handler = handlers.get(action)

        if not handler:
            logger.error("❌ Неизвестный action: %s", action)
            await utils.send_response(
                message, {"error": f"Неизвестный action: {action}"}
            )
        else:
            result = await handler()
            await utils.send_response(message, result)

    except json.JSONDecodeError as e:
        logger.error("❌ Ошибка декодирования JSON: %s", str(e))
        await utils.send_response(message, {"error": "Invalid JSON format"})
    except KeyError as e:
        logger.error("❌ Отсутствует обязательное поле: %s", str(e))
        await utils.send_response(
            message, {"error": f"Missing required field: {str(e)}"}
        )
    except Exception as e:
        logger.error("💀 Неожиданная ошибка: %s", str(e))
        await utils.send_response(message, {"error": "Internal server error"})


async def start_consuming():
    """
    Запускает обработку очередей RabbitMQ.

    Слушает очереди:
    - auth_queue: команды аутентификации
    - health_check: проверка работоспособности
    """
    try:
        logger.info("🚀 Запуск обработки сообщений...")

        # Создаем сервис аутентификации с сессией из контекстного менеджера
        async with SessionContextManager() as session_manager:
            auth_service = AuthenticationService(session_manager.session)
            user_service = UserService(session_manager.session)

        connection = await connect_robust(**config.rabbitmq_params)
        channel = await connection.channel()

        # Очереди для обработки
        queues = {
            "auth_queue": lambda msg: process_auth_message(
                msg, auth_service, user_service
            ),
            "health_check": health.handle_health_check,
        }

        for queue_name, handler in queues.items():
            queue = await channel.declare_queue(queue_name, auto_delete=True)
            await queue.consume(handler)
            logger.info("✅ Подключена очередь: %s", queue_name)

        logger.info("🎉 Обработчик сообщений запущен")

    except Exception as e:
        logger.error("💀 Ошибка запуска обработчика: %s", str(e))
        raise

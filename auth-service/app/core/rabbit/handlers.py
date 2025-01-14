"""
Модуль обработчиков сообщений RabbitMQ.

Обрабатывает сообщения из RabbitMQ:
- authenticate: аутентификация пользователя
- logout: выход из системы
- health_check: проверка работоспособности
"""
import json
from aio_pika import IncomingMessage, Message
from sqlalchemy import text
from app.core.dependencies import get_db_session
from pydantic_core import ValidationError
from app.schemas import AuthenticationSchema, CreateUserSchema, TokenSchema
from app.services import AuthenticationService, UserService
from app.core.exceptions import (
    UserNotFoundError,
    UserExistsError,
    InvalidEmailFormatError,
    WeakPasswordError
)

async def handle_authenticate(data: dict, auth_service: AuthenticationService) -> dict:
    """
    Обрабатывает сообщение аутентификации.

    Args:
        data: Данные для аутентификации
        auth_service: Сервис аутентификации

    Returns:
        Токен доступа и тип токена
    """
    try:
        auth_data_schema = AuthenticationSchema(**data)
        token: TokenSchema = await auth_service.authenticate(auth_data_schema)
        return {
            "status_code": 200,
            "access_token": token.access_token,
            "token_type": token.token_type
        }

    except (UserNotFoundError, UserExistsError,
            InvalidEmailFormatError, WeakPasswordError) as e:
        return {
            "status_code": getattr(e, "status_code", 400),
            "detail": str(e),
            "error_type": getattr(e, "error_type", "validation_error"),
            "extra": getattr(e, "extra", {})
        }

async def handle_logout(token: str, auth_service: AuthenticationService) -> dict:
    """
    Обрабатывает сообщение выхода.

    Args:
        token: Токен для выхода
        auth_service: Сервис аутентификации

    Returns:
        Сообщение об успешном выходе
    """
    return await auth_service.logout(token)

async def handle_oauth(
    provider: str,
    user_data: dict,
    auth_service: AuthenticationService
) -> dict:
    """
    Обрабатывает сообщение OAuth.

    Args:
        provider: Провайдер OAuth
        user_data: Данные пользователя от провайдера
        auth_service: Сервис аутентификации

    Returns:
        Токен доступа и тип токена
    """
    return await auth_service.oauth_authenticate(provider, user_data)

async def handle_register(
    data: dict,
    user_service: UserService
) -> dict:
    """
    Обрабатывает сообщение регистрации.

    Args:
        data: Данные пользователя для регистрации
        user_service: Сервис пользователей
        auth_service: Сервис аутентификации

    Returns:
        Токен доступа и тип токена
    """
    try:
        # Преобразуем dict в схему
        user_data_schema = CreateUserSchema(**data)
        user = await user_service.create_user(user_data_schema)

        return {
            "status_code": 201,
            "user_id": str(user["id"]),
            "email": user["email"]
        }

    except (ValidationError, UserExistsError,
            InvalidEmailFormatError, WeakPasswordError) as e:
        return {
            "status_code": getattr(e, "status_code", 400),
            "detail": str(e),
            "error_type": getattr(e, "error_type", "validation_error"),
            "extra": getattr(e, "extra", {})
        }

async def handle_health_check(message: IncomingMessage) -> None:
    try:
        async with get_db_session() as session:
            await session.execute(text("SELECT 1"))

            async with message.process():
                await message.channel.default_exchange.publish(
                    Message(
                        body=json.dumps({"status": "healthy"}).encode(),
                        content_type="application/json"
                    ),
                    routing_key=message.reply_to
                )
    except Exception:
        async with message.process():
            await message.channel.default_exchange.publish(
                Message(
                    body=json.dumps({"status": "unhealthy"}).encode(),
                    content_type="application/json"
                ),
                routing_key=message.reply_to
            )

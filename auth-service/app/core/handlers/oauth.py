"""
Модуль обработки сообщений аутентификации OAuth.
"""

import logging

from app.services import AuthService

logger = logging.getLogger(__name__)


async def handle_oauth(
    provider: str, user_data: dict, auth_service: AuthService
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
    logger.info(
        "🔑 Попытка OAuth аутентификации через %s: %s", provider, user_data.get("email")
    )
    try:
        result = await auth_service.oauth_authenticate(provider, user_data)
        logger.info("✅ OAuth аутентификация успешна для %s", user_data.get("email"))
        return result
    except Exception as e:
        logger.error("❌ Ошибка OAuth аутентификации: %s", str(e))
        return {"status_code": 500, "detail": str(e), "error_type": "oauth_error"}

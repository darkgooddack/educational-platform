"""
Модуль зависимостей для аутентификации.

Содержит функции-зависимости для работы с токенами и текущим пользователем.
"""

import logging

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import config
from app.schemas import UserCredentialsSchema
from app.core.dependencies.redis import get_redis
from app.core.storages.redis.auth import AuthRedisStorage
from app.core.exceptions.v1.auth.security import TokenInvalidError

logger = logging.getLogger(__name__)

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl=config.auth_url, 
    auto_error=False,
    scheme_name="OAuth2PasswordBearer"
)


async def get_current_user(
    token: str = Depends(oauth2_schema),
) -> UserCredentialsSchema:
    """
    Получает данные текущего пользователя.

    Args:
        token: Токен доступа.

    Returns:
        Данные текущего пользователя.
    """
    logger.debug("Начало получения текущего пользователя")
    logger.debug("Получен токен: %s", token)

    if not token:
        logger.debug("Токен отсутствует в запросе")
        raise TokenInvalidError()

    auth_storage = AuthRedisStorage()
    logger.debug("Создан экземпляр AuthRedisStorage")
    
    try:
        user = await auth_storage.verify_and_get_user(token)
        logger.debug("Пользователь успешно получен: %s", user)
        return user
        
    except Exception as e:
        logger.debug("Ошибка при получении пользователя: %s", str(e))
        raise TokenInvalidError()

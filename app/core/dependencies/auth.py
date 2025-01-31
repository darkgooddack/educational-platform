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
    logger.debug("Получен токен: %s", token)
    auth_storage = AuthRedisStorage()
    user = await auth_storage.verify_and_get_user(token)
    if user is None:
        raise TokenInvalidError()
    
    return user

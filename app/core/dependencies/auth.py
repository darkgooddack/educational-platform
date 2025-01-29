"""
Модуль зависимостей для аутентификации.

Содержит функции-зависимости для работы с токенами и текущим пользователем.
"""

import logging

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import config
from app.schemas import UserCredentialsSchema
from app.services.v1.auth.service import AuthDataManager

logger = logging.getLogger(__name__)

oauth2_schema = OAuth2PasswordBearer(tokenUrl=config.auth_url, auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_schema),
    data_manager: AuthDataManager = Depends(),
) -> UserCredentialsSchema | None:
    """
    Получает данные текущего пользователя.

    Args:
        token: Токен доступа.

    Returns:
        Данные текущего пользователя.
    """
    logger.debug("Получен токен: %s", token)

    return await data_manager.verify_and_get_user(token)

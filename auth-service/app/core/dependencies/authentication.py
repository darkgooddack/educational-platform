"""
Модуль зависимостей для аутентификации.

Содержит функции-зависимости для работы с токенами и текущим пользователем.
"""
import logging
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.schemas import UserSchema
from app.services import AuthenticationDataManager
from app.core.config import config


logger = logging.getLogger(__name__)

oauth2_schema = OAuth2PasswordBearer(tokenUrl=config.auth_url, auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_schema),
    data_manager: AuthenticationDataManager = Depends()
) -> UserSchema | None:
    """
    Получает данные текущего пользователя.

    Args:
        token: Токен доступа.

    Returns:
        Данные текущего пользователя.
    """
    logger.debug("Получен токен: %s", token)

    return await data_manager.verify_and_get_user(token)

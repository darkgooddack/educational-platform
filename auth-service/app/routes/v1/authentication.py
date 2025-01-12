"""
Роутер аутентификации пользователей.

Предоставляет эндпоинты для входа и выхода из системы.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.dependencies.authentication import oauth2_schema
from app.core.dependencies.database import get_db_session
from app.schemas import AuthenticationSchema, TokenSchema
from app.services import AuthenticationService
from app.core.config import config
from app.core.exceptions import (
    UserNotFoundError,
    InvalidCredentialsError,
    InvalidPasswordError,
)
router = APIRouter(**config.SERVICES["authentication"].to_dict())

@router.post("")
async def authenticate(
    credentials: AuthenticationSchema,
    session: AsyncSession = Depends(get_db_session),
) -> TokenSchema | None:
    """
    Аутентифицирует пользователя по email и возвращает JWT токен.

    Args:
        credentials: Данные для аутентификации
        session: Сессия базы данных

    Returns:
        TokenSchema с access_token и token_type

    Raises:
        UserNotFoundError: Если пользователь не найден

    """
    try:
        return await AuthenticationService(session).authenticate(credentials)
    except UserNotFoundError as e:
        raise UserNotFoundError("email", credentials.email) from e
    except InvalidCredentialsError as e:
        raise InvalidPasswordError() from e

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_schema),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Выполняет выход пользователя из системы.

    Args:
        token: JWT токен пользователя
        session: Сессия базы данных

    Returns:
        Словарь с сообщением об успешном выходе {"message": "Выход выполнен успешно!"}
    """
    return await AuthenticationService(session).logout(token)

"""
Роутер регистрации пользователей.

Предоставляет эндпоинты для регистрации новых пользователей.
"""

from fastapi import APIRouter, Depends
from pydantic_core import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.dependencies.database import get_db_session
from app.core.exceptions import InvalidEmailFormatError, WeakPasswordError
from app.schemas import CreateUserSchema
from app.services import UserService

router = APIRouter(**config.SERVICES["registration"].to_dict())


@router.post("/")
async def registration_user(
    user: CreateUserSchema,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Регистрация нового пользователя

    Args:
        user: Данные пользователя (email, password)
        session: Сессия БД

    Returns:
        None

    Raises:
        WeakPasswordError: Слабый пароль
        InvalidEmailFormatError: Неверный формат email
    """
    try:
        return await UserService(session).create_user(user)
    except ValidationError as e:
        if "password" in str(e):
            raise WeakPasswordError() from e
        elif "email" in str(e):
            raise InvalidEmailFormatError(user.email) from e
        raise e

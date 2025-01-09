from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic_core import ValidationError

from api.errors.v1.users import (
    WeakPasswordError,
    InvalidEmailFormatError,
)
from api.core.database.session import get_db_session
from api.schemas.v1.users import UserSchema
from api.services.v1.users import RegistrationService
from api.core.config import app_config

router = APIRouter(**app_config.SERVICES["registration"].to_dict())

@router.post("/")
async def registration_user(
    user: UserSchema,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """
    Регистрация нового пользователя
    #! Для примера
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
        return await RegistrationService(session).create_user(user)
    except ValidationError as e:
        if "password" in str(e):
            raise WeakPasswordError() from e
        elif "email" in str(e):
            raise InvalidEmailFormatError(user.email) from e
        raise e
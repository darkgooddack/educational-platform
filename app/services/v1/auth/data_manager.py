from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserModel
from app.schemas import UserSchema
from app.services.v1.base import BaseEntityManager


class AuthDataManager(BaseEntityManager[UserSchema]):
    """
    Класс для работы с данными пользователей в базе данных.

    Args:
        session: Асинхронная сессия для работы с базой данных.
        schema: Схема данных пользователя.
        model: Модель данных пользователя.

    """

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, schema=UserSchema, model=UserModel)

    async def get_user_by_credentials(self, email: str) -> Optional[UserModel]:
        """
        Получение пользователя по учетным данным

        Args:
            email: Электронная почта пользователя.

        Returns:
            Пользователь или None, если полользователь не найден.
        """
        return await self.get_user_by_field("email", email)

    async def update_online_status(self, user_id: int, is_online: bool) -> None:
        """
        Обновляет онлайн статус пользователя
        """
        await self.update_fields(
            user_id,
            {
                "is_online": is_online,
                "last_seen": datetime.now(timezone.utc) if not is_online else None
            }
        )

    async def update_last_seen(self, user_id: int) -> None:
        """
        Обновляет время последнего визита
        """
        await self.update_fields(
            user_id,
            {
                "last_seen": datetime.now(timezone.utc)
            }
        )

# TODO: Добавить методы для работы с данными пользователей, ниже приведены примеры методов
# async def update_last_login(self, user_id: int) -> None:
#     """
#     Обновление времени последнего входа

#     Args:
#         user_id: Идентификатор пользователя.

#     Returns:
#         None
#     """
#     await self.update_fields(
#         user_id,
#         {"last_login": datetime.now(timezone.utc)}
#     )

# async def increment_login_attempts(self, user_id: int) -> int:
#     """
#     Увеличение счетчика попыток входа

#     Args:
#         user_id: Идентификатор пользователя.

#     Returns:
#         Количество попыток входа.
#     """
#     user = await self.get_by_id(user_id)
#     attempts = (user.login_attempts or 0) + 1
#     await self.update_fields(user_id, {"login_attempts": attempts})
#     return attempts

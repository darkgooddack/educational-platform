from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User as UserSQLAlchemy
from typing import List, Optional
from ..interfaces.i_user_repository import IUserRepository
from ..core.exceptions import AppException

class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_phone(self, phone_number: str) -> Optional[UserSQLAlchemy]:
        try:
            result = await self.session.execute(
                select(UserSQLAlchemy).where(UserSQLAlchemy.phone_number == phone_number)
            )
            return result.scalars().first()
        except SQLAlchemyError as exc:
            raise AppException(f"DatabaseError: {str(exc)}")

    async def create_user(self, name: str, email: str, phone_number: str, hashed_password: str, role: str) -> UserSQLAlchemy:
        try:
            new_user = UserSQLAlchemy(
                name=name,
                email=email,
                phone_number=phone_number,
                role=role,
            )
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
        except SQLAlchemyError as exc:
            raise AppException(f"Error creating user: {str(exc)}")

    async def get_all_users(self) -> List[UserSQLAlchemy]:
        try:
            result = await self.session.execute(select(UserSQLAlchemy))
            return result.scalars().all()
        except SQLAlchemyError as exc:
            raise AppException(f"Error retrieving all users: {str(exc)}")

    async def get_user_by_id(self, user_id: int) -> Optional[UserSQLAlchemy]:
        try:
            result = await self.session.execute(
                select(UserSQLAlchemy).where(UserSQLAlchemy.id == user_id)
            )
            user = result.scalars().first()
            return user
        except SQLAlchemyError as exc:
            raise AppException(f"Error retrieving user: {str(exc)}")

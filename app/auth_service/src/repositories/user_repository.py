from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
from ..models.user import User
from ..core.exceptions import DatabaseException, UserNotFoundException, UserAlreadyExistsException
from ..interfaces.i_user_repository import IUserRepository

class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            stmt = select(User).options(selectinload(User.tokens)).where(User.email == email)
            result = await self.session.execute(stmt)
            user = result.scalars().first()
            if not user:
                return None
            
            return user
        except SQLAlchemyError as e:
            raise DatabaseException("Error retrieving user by email.") from e

    async def get_user_with_tokens(self, user_id: int) -> Optional[User]:
        try:
            stmt = select(User).options(selectinload(User.tokens)).where(User.id == int(user_id))
            result = await self.session.execute(stmt)
            user = result.scalars().first()
            if not user:
                raise UserNotFoundException(f"User with ID {user_id} not found.")
            return user
        except UserNotFoundException as e:
            raise e
        except SQLAlchemyError as e:
            raise DatabaseException("Error retrieving user with tokens.") from e

    async def add_user(self, user: User) -> None:
        try:
            existing_user = await self.get_user_by_email(user.email)
            if existing_user:
                raise UserAlreadyExistsException(f"User with email {user.email} already exists.")
            self.session.add(user)
            await self.session.commit()
        except UserAlreadyExistsException as e:
            raise e
        except SQLAlchemyError as e:
            raise DatabaseException("Error adding user to the database.") from e

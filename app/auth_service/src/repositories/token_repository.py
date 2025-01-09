from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from datetime import datetime
from typing import Optional
from ..models.user import UserToken
from ..utils.logger import logger
from ..core.exceptions import DatabaseException
from ..interfaces.i_token_repository import ITokenRepository

class TokenRepository(ITokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_token_user_by_access(self, user_token_id: int, user_id: int, access_token: str) -> Optional[UserToken]:
        try:
            stmt = (
                select(UserToken)
                .options(joinedload(UserToken.user))
                .where(
                    UserToken.id == user_token_id,
                    UserToken.user_id == user_id,
                    UserToken.access_token == access_token,
                    UserToken.expires_at > datetime.utcnow()
                )
            )
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching token by access: {e}", exc_info=True)
            raise DatabaseException("Error retrieving token user by access.") from e

    async def add_token(self, user_token: UserToken) -> None:
        try:
            self.session.add(user_token)
            await self.session.commit()
        except SQLAlchemyError as e:
            raise DatabaseException("Error adding token to the database.") from e

    async def get_user_token(self, refresh_token: str, access_token: str, user_id: int) -> Optional[UserToken]:
        try:
            stmt = select(UserToken).options(joinedload(UserToken.user)).where(
                UserToken.refresh_token == refresh_token,
                UserToken.access_token == access_token,
                UserToken.user_id == user_id
            )
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching user token: {e}", exc_info=True)
            raise DatabaseException("Error retrieving user token.") from e

    async def update_token(self, user_token: UserToken) -> None:
        try:
            self.session.add(user_token)
            await self.session.commit()
        except SQLAlchemyError as e:
            raise DatabaseException("Error updating token in the database.") from e

    async def get_token_by_user_id(self, user_id: int) -> Optional[UserToken]:
        try:
            stmt = select(UserToken).where(UserToken.user_id == user_id)
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching token by user ID: {e}", exc_info=True)
            raise DatabaseException("Error retrieving token by user ID.") from e

    async def delete_tokens_by_user_id(self, user_id: int) -> None:
        try:
            stmt = select(UserToken).where(UserToken.user_id == user_id)
            result = await self.session.execute(stmt)
            tokens = result.scalars().all()
            for token in tokens:
                await self.session.delete(token)
            await self.session.commit()
        except SQLAlchemyError as e:
            raise DatabaseException("Error deleting tokens by user ID.") from e

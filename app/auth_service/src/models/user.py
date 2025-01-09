from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ..db.session import Base
 
class User(Base):
    __tablename__ = "users_auth"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=False)

    tokens = relationship("UserToken", back_populates="user")
    
    @classmethod
    async def get_user_with_tokens(cls, session: AsyncSession, user_id: int):
        stmt = select(cls).options(
            selectinload(cls.tokens)
        ).where(cls.id == user_id)
        
        result = await session.execute(stmt)
        return result.scalars().first()

class UserToken(Base):
    __tablename__ = "user_tokens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users_auth.id'), nullable=False)
    access_token = Column(String(250), nullable=True)
    refresh_token = Column(String(250), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="tokens")
    
    @classmethod
    async def get_token_with_user(cls, session: AsyncSession, token_id: int):
        stmt = select(cls).options(
            selectinload(cls.user)
        ).where(cls.id == token_id)
        
        result = await session.execute(stmt)
        return result.scalars().first()
    
    
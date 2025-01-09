from ..db.session import Base
from sqlalchemy.orm import joinedload
from sqlalchemy import Column, Integer, String, DateTime, func, select, Enum
from sqlalchemy.ext.asyncio import AsyncSession

class User(Base):
    __tablename__ = "users_register"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    phone_number = Column(String, nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(Enum("student", "teacher", "professor", name="user_roles"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    @classmethod
    async def get_user_with_tokens(cls, session: AsyncSession, email: str):
        stmt = select(cls).options(
            joinedload(cls.tokens)
        ).where(cls.email == email)
        result = await session.execute(stmt)
        return result.scalars().first()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone_number": self.phone_number,
            "email": self.email,
            "role": self.role, 
            "created_at": self.created_at.isoformat()
        }
    
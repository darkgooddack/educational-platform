from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import async_session_maker
from typing import AsyncGenerator
from ...core.exceptions import DependencyException

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with async_session_maker() as session:
            yield session
    except Exception as e:
        raise DependencyException(f"Error initializing async session: {str(e)}")
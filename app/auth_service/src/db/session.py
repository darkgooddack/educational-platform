from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from ..core.config import settings
from sqlalchemy import NullPool

if settings().MODE == "TEST":
    DATABASE_URL = f"postgresql+asyncpg://{settings().TEST_DB_USER}:{settings().TEST_DB_PASS}@{settings().TEST_DB_HOST}:{settings().TEST_DB_PORT}/{settings().TEST_DB_NAME}"
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_URL = f"postgresql+asyncpg://{settings().POSTGRES_USER}:{settings().POSTGRES_PASS}@{settings().POSTGRES_HOST}:{settings().POSTGRES_PORT}/{settings().POSTGRES_DB}"
    DATABASE_PARAMS = {}

class Base(DeclarativeBase):
    pass

metadata = Base.metadata

engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


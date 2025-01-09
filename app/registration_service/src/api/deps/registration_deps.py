from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .session_deps import get_async_session
from ...interfaces.i_user_repository import IUserRepository
from ...repositories.user_repository import UserRepository
from ...services.user_service import UserService
from ...api.deps.auth_service_deps import get_auth_service_client
from ...core.exceptions import DependencyException
from ...interfaces.i_user_service import IUserService

async def get_user_repository(
        session: AsyncSession = Depends(get_async_session),
) -> IUserRepository:
    try:
        return UserRepository(session)
    except Exception as e:
        raise DependencyException(f"Error initializing UserRepository: {e}")

async def get_user_service(
        user_repository: IUserRepository = Depends(get_user_repository),
        auth_service_client = Depends(get_auth_service_client),
) -> IUserService:
    try:
        return UserService(user_repository, auth_service_client)
    except Exception as e:
        raise DependencyException(f"Error initializing UserService: {e}")
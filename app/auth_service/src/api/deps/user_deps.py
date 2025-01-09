from ...services.registration_service import RegistrationService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.security import oauth2_scheme
from ...services.auth_service import AuthService
from ...repositories.user_repository import UserRepository
from ...services.token_service import TokenService
from ...repositories.token_repository import TokenRepository
from .session_deps import get_async_session
from ...interfaces.i_token_repository import ITokenRepository
from ...interfaces.i_user_repository import IUserRepository
from ...interfaces.i_token_service import ITokenService
from ...interfaces.i_auth_service import IAuthService
from ...interfaces.i_registration_service import IRegistrationService
from ...core.exceptions import DependencyException, InvalidTokenException

async def get_token_repository(
    session: AsyncSession = Depends(get_async_session),
) -> ITokenRepository:
    try:
        return TokenRepository(session)
    except Exception as e:
        raise DependencyException(f"Error initializing TokenRepository: {e}")

async def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IUserRepository:
    try:
        return UserRepository(session)
    except Exception as e:
        raise DependencyException(f"Error initializing UserRepository: {e}")

async def get_token_service(
    token_repo: TokenRepository = Depends(get_token_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> ITokenService:
    try:
        return TokenService(token_repo, user_repo)
    except Exception as e:
        raise DependencyException(f"Error initializing TokenService: {e}")

async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    token_service: TokenService = Depends(get_token_service),
) -> IAuthService:
    try:
        return AuthService(user_repo, token_service)
    except Exception as e:
        raise DependencyException(f"Error initializing AuthService: {e}")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user = await auth_service.get_token_user(token)
        if not user:
            raise InvalidTokenException("Invalid or expired token.")
        return user
    except Exception as e:
        raise DependencyException(f"Error verifying user: {str(e)}")

async def get_registration_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> IRegistrationService:
    try:
        return RegistrationService(user_repo=user_repo)
    except Exception as e:
        raise DependencyException(f"Error initializing RegistrationService: {e}")



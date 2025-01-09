from typing import Optional
from ..models.user import User
from ..api.schemas.token import UserTokenDTO
from ..core.security import verify_password
from ..interfaces.i_user_repository import IUserRepository
from ..interfaces.i_token_service import ITokenService
from ..core.exceptions import AppException, UserNotFoundException, InvalidTokenException, UserAuthenticationException, InvalidTokenException
from ..interfaces.i_auth_service import IAuthService

class AuthService(IAuthService):
    def __init__(
        self,
        user_repo: IUserRepository,
        token_service: ITokenService,
    ):
        self.user_repo = user_repo
        self.token_service = token_service

    async def authenticate_user(self, email: str, password: str) -> Optional[UserTokenDTO]:
        try:
            user = await self.user_repo.get_user_by_email(email)
            if not user:
                raise UserNotFoundException("User not found.")

            if not verify_password(password, user.password):
                raise UserAuthenticationException("Invalid email or password.")

            tokens = await self.token_service.generate_tokens(user)
            user_token = await self.token_service.get_user_token(user.id)

            if not user_token:
                raise InvalidTokenException()

            return UserTokenDTO(
                id=user_token.id,
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                expires_at=user_token.expires_at,
            )
        
        except Exception as e:
            raise AppException(f"An unexpected error occurred: {str(e)}.")

    async def refresh_tokens(self, refresh_token: str) -> dict:
        try:
            tokens = await self.token_service.refresh_tokens(refresh_token)
            if not tokens:
                raise InvalidTokenException("Invalid or expired refresh token.")
            return tokens
        
        except Exception as e:
            raise e

    async def get_token_user(self, token: str) -> Optional[User]:
        try:
            user = await self.token_service.validate_and_get_user(token)
            if not user:
                raise UserNotFoundException("User not found.")
            return user
        
        except Exception as e:
            raise e

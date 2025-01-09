from datetime import datetime, timedelta
from typing import Optional
from ..models.user import User, UserToken
from ..core.security import generate_token, get_token_payload, str_encode, str_decode
from ..interfaces.i_token_repository import ITokenRepository
from ..interfaces.i_user_repository import IUserRepository
from ..core.config import settings
from ..utils.string_utils import unique_string
from ..core.exceptions import (
    DatabaseException, 
    TokenGenerationException, 
    TokenExpiredException, 
    InvalidTokenException, 
    AppException, 
    UserNotFoundException
    )
from ..interfaces.i_token_service import ITokenService

class TokenService(ITokenService):
    def __init__(
        self,
        token_repo: ITokenRepository,
        user_repo: IUserRepository,
    ):
        self.token_repo = token_repo
        self.user_repo = user_repo

    async def generate_tokens(self, user: User) -> dict:
        try:
            await self.token_repo.delete_tokens_by_user_id(user.id)

            refresh_token = unique_string(100)
            access_token = unique_string(50)

            rt_expires = timedelta(minutes=settings().REFRESH_TOKEN_EXPIRE_MINUTES)
            at_expires = timedelta(minutes=settings().ACCESS_TOKEN_EXPIRE_MINUTES)

            user_token = UserToken(
                user_id=user.id,
                refresh_token=refresh_token,
                access_token=access_token,
                expires_at=datetime.utcnow() + rt_expires,
            )
            await self.token_repo.add_token(user_token)

            access_payload = {
                "sub": str_encode(str(user.id)),
                "a": access_token,
                "r": str_encode(str(user_token.id)),
            }
            refresh_payload = {
                "sub": str_encode(str(user.id)),
                "t": refresh_token,
                "a": access_token,
            }

            access_token = generate_token(
                access_payload, settings().JWT_SECRET, settings().JWT_ALGORITHM, at_expires
            )
            refresh_token = generate_token(
                refresh_payload, settings().SECRET_KEY, settings().JWT_ALGORITHM, rt_expires
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": at_expires.seconds,
            }

        except DatabaseException as e:
            raise TokenGenerationException("Database error while generating tokens.") from e
        except Exception as e:
            raise TokenGenerationException("Unexpected error during token generation.") from e

    async def refresh_tokens(self, refresh_token: str) -> dict:
        try:
            token_payload = get_token_payload(refresh_token, settings().SECRET_KEY, settings().JWT_ALGORITHM)
            if not token_payload:
                raise InvalidTokenException

            user_id = str_decode(token_payload.get("sub"))
            user_token = await self.token_repo.get_user_token(
                token_payload.get("t"), token_payload.get("a"), int(user_id)
            )

            if not user_token:
                raise InvalidTokenException("Token not found.")
            if user_token.expires_at <= datetime.utcnow():
                raise TokenExpiredException()

            return await self.generate_tokens(user_token.user)

        except AppException:
            raise
        except Exception as e:
            raise TokenGenerationException("Unexpected error during token refresh.") from e

    async def validate_and_get_user(self, token: str) -> Optional[User]:
        try:
            payload = get_token_payload(token, settings().JWT_SECRET, settings().JWT_ALGORITHM)
            if not payload:
                raise InvalidTokenException()

            user_id = str_decode(payload.get("sub"))
            user = await self.user_repo.get_user_with_tokens(user_id)
            if not user:
                raise UserNotFoundException("User not found.")

            return user

        except AppException:
            raise
        except Exception as e:
            raise TokenGenerationException("Unexpected error during token validation.") from e

    async def get_user_token(self, user_id: int) -> Optional[UserToken]:
        try:
            return await self.token_repo.get_token_by_user_id(user_id)
        except DatabaseException as e:
            raise TokenGenerationException("Database error while fetching user token.") from e
        except Exception as e:
            raise TokenGenerationException("Unexpected error during token fetching.") from e

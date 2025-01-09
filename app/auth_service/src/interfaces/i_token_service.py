from typing import Protocol, Optional
from ..models.user import User, UserToken

class ITokenService(Protocol):
    async def generate_tokens(self, user: User) -> dict:
        ...
        
    async def refresh_tokens(self, refresh_token: str) -> dict:
        ...
        
    async def validate_and_get_user(self, token: str) -> Optional[User]:
        ...
        
    async def get_user_token(self, user_id: int) -> Optional[UserToken]:
        ...
        
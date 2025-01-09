from typing import Protocol, Optional
from ..models.user import User
from ..api.schemas.user import UserTokenDTO

class IAuthService(Protocol):
    async def authenticate_user(self, email: str, password: str) -> Optional[UserTokenDTO]:
        ...

    async def refresh_tokens(self, refresh_token: str) -> dict:
        ...

    async def get_token_user(self, token: str) -> Optional[User]:
        ...

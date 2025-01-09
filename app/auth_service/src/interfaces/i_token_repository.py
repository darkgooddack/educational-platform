from typing import Protocol, Optional
from ..models.user import UserToken

class ITokenRepository(Protocol):
    async def get_token_user_by_access(self, user_token_id: int, user_id: int, access_token: str) -> Optional[UserToken]:
        ...

    async def add_token(self, user_token: UserToken) -> None:
        ...

    async def get_user_token(self, refresh_token: str, access_token: str, user_id: str) -> Optional[UserToken]:
        ...

    async def update_token(self, user_token: UserToken) -> None:
        ...

    async def get_token_by_user_id(self, user_id: int) -> Optional[UserToken]:
        ...

    async def delete_tokens_by_user_id(self, user_id: int) -> None:
        ...

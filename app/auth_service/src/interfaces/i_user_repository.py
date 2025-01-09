from typing import Protocol, Optional
from ..models.user import User

class IUserRepository(Protocol):
    async def get_user_by_email(self, email: str) -> Optional[User]:
        ...

    async def get_user_with_tokens(self, user_id: int) -> Optional[User]:
        ...

    async def add_user(self, user: User) -> None:
        ...

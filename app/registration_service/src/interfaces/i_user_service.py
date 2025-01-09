from ..api.schemas.user import RegisterUserRequestDTO
from typing import Protocol, Any, List
from ..models.user import User

class IUserService(Protocol):
    async def register_user(self, data: RegisterUserRequestDTO) -> Any:
        ...

    async def get_all_users(self) -> List[Any]:
        ...

    async def get_user_by_id(self, user_id) -> User:
        ...

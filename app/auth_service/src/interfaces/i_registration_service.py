from typing import Protocol
from ..api.schemas.user import RegisterUserRequestDTO
from ..models.user import User

class IRegistrationService(Protocol):
    async def register_user(self, data: RegisterUserRequestDTO) -> User:
        ...
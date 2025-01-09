from typing import Protocol

class IExternalUserService(Protocol):
    async def get_user_from_registration_service(self, email: str) -> dict:
        ...
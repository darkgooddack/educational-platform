from abc import ABC, abstractmethod

class IExternalUserService(ABC):
    @abstractmethod
    async def get_user_from_registration_service(self, email: str) -> dict:
        pass
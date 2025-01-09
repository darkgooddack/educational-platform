from typing import Protocol, Dict, Any

class IAuthServiceClient(Protocol):
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        ...
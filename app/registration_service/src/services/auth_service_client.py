import httpx
from typing import Dict, Any
from ..interfaces.i_auth_service_client import IAuthServiceClient
from ..core.exceptions import ExternalServiceException

class AuthServiceClient(IAuthServiceClient):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/users", json=user_data)

                if response.status_code != 201:
                    raise ExternalServiceException(
                        f"Failed to create account. Status code: {response.status_code}, Response: {response.text}"
                    )
                
                return response.json()
        except httpx.RequestError as exc:
            raise ExternalServiceException(
                f"Error during request to auth service: {str(exc)}"
            )
        except Exception as exc:
            raise ExternalServiceException(
                f"Unexpected error in AuthServiceClient: {str(exc)}"
            )

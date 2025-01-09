import httpx
from ..core.exceptions import ExternalServiceException, UserFetchFailedException
from ..core.config import settings
from ..interfaces.i_external_user_service import IExternalUserService

class ExternalUserService(IExternalUserService):
    async def get_user_from_registration_service(self, email: str) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{settings().REGISTRATION_SERVICE_URL}/users/{email}")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise ExternalServiceException(
                    "RegistrationService",
                    f"Request error occurred: {str(e)}"
                ) from e
            except httpx.HTTPStatusError as e:
                raise UserFetchFailedException(
                    f"Error response from registration service: {e.response.text}"
                ) from e
            except Exception as e:
                raise ExternalServiceException(
                    "RegistrationService",
                    "Unexpected error occurred while communicating with the registration service."
                ) from e
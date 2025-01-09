from ...services.auth_service_client import AuthServiceClient
from ...interfaces.i_auth_service_client import IAuthServiceClient
from ...core.config import settings
from ...core.exceptions import DependencyException

async def get_auth_service_client() -> IAuthServiceClient:
    try:
        return AuthServiceClient(base_url=settings().AUTH_SERVICE_URL)
    except Exception as e:
        raise DependencyException(f"Error initializing AuthServiceClient: {e}")
from ..api.schemas.user import RegisterUserRequestDTO
from ..core.security import hash_password
from ..interfaces.i_user_repository import IUserRepository
from ..interfaces.i_auth_service_client import IAuthServiceClient
from ..interfaces.i_user_service import IUserService
from ..core.exceptions import UserAlreadyExistsException, ExternalServiceException, AppException, UserNotFoundException
from typing import List, Any
from ..models.user import User

class UserService(IUserService):
    def __init__(self, user_repository: IUserRepository, auth_service_client: IAuthServiceClient):
        self.user_repository = user_repository
        self.auth_service_client = auth_service_client

    async def register_user(self, data: RegisterUserRequestDTO) -> Any:
        try:
            existing_user = await self.user_repository.get_user_by_phone(data.phone_number)
            if existing_user:
                raise UserAlreadyExistsException()
            
            hashed_password = hash_password(data.password)
            new_user = await self.user_repository.create_user(
                name=data.name,
                email=data.email,
                phone_number=data.phone_number,
                hashed_password=hashed_password,
                role=data.role,
            )

            try:
                await self.auth_service_client.create_user({
                    "name": data.name,
                    "email": data.email,
                    "password": data.password,
                    "phone_number": data.phone_number,
                    "role": data.role,
                })
            except Exception as exc:
                raise ExternalServiceException(str(exc))

            return new_user
        except AppException as exc:
            raise exc
        except Exception as exc:
            raise AppException(f"Unexpected error: {str(exc)}")
    
    async def get_all_users(self) -> List[Any]:
        try:
            return await self.user_repository.get_all_users()
        except Exception as exc:
            raise AppException(f"Failed to retrieve users: {str(exc)}")

    async def get_user_by_id(self, user_id: int) -> User:
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                raise UserNotFoundException("User not found")
            return user
        except Exception as exc:
            raise AppException(f"Failed to fetch user: {str(exc)}")

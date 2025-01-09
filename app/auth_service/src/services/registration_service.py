from ..models.user import User
from ..api.schemas.user import RegisterUserRequestDTO
from ..core.security import hash_password
from ..core.exceptions import UserAlreadyExistsException, DatabaseException, AppException
from ..interfaces.i_user_repository import IUserRepository
from ..interfaces.i_registration_service import IRegistrationService

class RegistrationService(IRegistrationService):
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def register_user(self, data: RegisterUserRequestDTO) -> User:
        try:
            existing_user = await self.user_repo.get_user_by_email(data.email)
            if existing_user:
                raise UserAlreadyExistsException("User with this email already exists.")
            
            hashed_password = hash_password(data.password)

            new_user = User(
                email=data.email,
                password=hashed_password,
                is_active=True,
            )

            await self.user_repo.add_user(new_user)
            return new_user

        except DatabaseException as e:
            raise
        except Exception as e:
            raise AppException("An unexpected error occurred.") from e

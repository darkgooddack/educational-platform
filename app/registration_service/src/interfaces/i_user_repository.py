from typing import Protocol, List, Optional
from ..models.user import User as UserSQLAlchemy

class IUserRepository(Protocol):
    async def get_user_by_phone(self, phone_number: str) -> Optional[UserSQLAlchemy]:
        ...
        
    async def create_user(self, name: str, email: str, phone_number: str, hashed_password: str, role: str) -> UserSQLAlchemy:
        ...
        
    async def get_all_users(self) -> List[UserSQLAlchemy]:
        ...
        
    async def get_user_by_id(self, user_id: int) -> Optional[UserSQLAlchemy]:
        ...
        
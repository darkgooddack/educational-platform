from pydantic import EmailStr
from typing import Optional, Any, List
from ...api.schemas.base import BaseResponse
from ...api.schemas.token import UserTokenDTO

class LoginResponseDTO(BaseResponse):
    access_token: str
    refresh_token: str
    expires_at: Any
    token_type: str = "Bearer"

    class Config:
        orm_mode = True
    
class RegisterUserRequestDTO(BaseResponse):
    name: str
    email: EmailStr
    password: str
    phone_number: str

    class Config:
        orm_mode = True
    
class RegisterUserResponseDTO(BaseResponse):
    id: int
    name: str
    email: EmailStr
    phone_number: str

    class Config:
        orm_mode = True
    
class UserBase(BaseResponse):
    email: str
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True
    
class User(UserBase):
    id: int
    is_active: bool
    tokens: List[UserTokenDTO]

    class Config:
        orm_mode = True
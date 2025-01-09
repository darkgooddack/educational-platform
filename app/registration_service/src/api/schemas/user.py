from pydantic import EmailStr
from typing import Optional
from .base import BaseResponse

class UserResponseDTO(BaseResponse):
    id: int
    email: str
    name: str
    phone_number: str
    role: str
    created_at: Optional[str]

    class Config:
        orm_mode = True
    
class RegisterUserRequestDTO(BaseResponse):
    name: str
    email: EmailStr
    password: str
    phone_number: str
    role: str
    
class VerifyUserRequestDTO(BaseResponse):
    token: str
    email: str
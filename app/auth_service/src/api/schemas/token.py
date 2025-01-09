from ...api.schemas.base import BaseResponse
from typing import Any

class UserTokenDTO(BaseResponse):
    id: int
    access_token: str
    refresh_token: str
    expires_at: Any

    class Config:
        orm_mode = True
    
class TokenResponseDTO(BaseResponse):
    access_token: str
    refresh_token: str
    expires_at: Any
    
    class Config:
        orm_mode = True

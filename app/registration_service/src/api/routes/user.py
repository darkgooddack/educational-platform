from fastapi import APIRouter, status, Depends, HTTPException
from ...api.schemas.user import RegisterUserRequestDTO, UserResponseDTO
from ...interfaces.i_user_service import IUserService
from ...api.deps.registration_deps import get_user_service
from ...core.exceptions import UserAlreadyExistsException, AppException
from typing import List

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@user_router.post("", status_code=status.HTTP_201_CREATED, response_model=UserResponseDTO)
async def register_user(
    data: RegisterUserRequestDTO,
    user_service: IUserService = Depends(get_user_service)
):
    try:
        new_user = await user_service.register_user(data)
        return UserResponseDTO(**new_user.to_dict())
    except UserAlreadyExistsException as exc:
        raise HTTPException(status_code=400, detail=exc.message)
    except AppException as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@user_router.get("/all", response_model=List[UserResponseDTO]) 
async def get_users(user_service: IUserService = Depends(get_user_service)):
    try:
        users = await user_service.get_all_users()
        return [UserResponseDTO(**user.to_dict()) for user in users]
    except AppException as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    
@user_router.get("/{user_id}", response_model=UserResponseDTO, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, user_service: IUserService = Depends(get_user_service)):
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponseDTO(**user.to_dict())
    except AppException as exc:
        raise HTTPException(status_code=500, detail=str(exc))

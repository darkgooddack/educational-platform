from fastapi import APIRouter, Depends, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from ...api.schemas.user import (
    LoginResponseDTO, 
    RegisterUserRequestDTO, 
    RegisterUserResponseDTO, 
    User as UserPydantic
)
from ...api.deps.user_deps import (
    get_current_user, 
    get_async_session, 
    get_auth_service, 
    get_registration_service
)
from ...models.user import User as UserSQLAlchemy
from ...interfaces.i_auth_service import IAuthService
from ...interfaces.i_registration_service import IRegistrationService
from ...core.exceptions import AppException
from ...core.exceptions_handler import app_exceptions_handler

auth_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@auth_router.post("/login", response_model=LoginResponseDTO)
async def user_login(
    data: OAuth2PasswordRequestForm = Depends(), 
    auth_service: IAuthService = Depends(get_auth_service)
):
    try:
        token = await auth_service.authenticate_user(data.username, data.password)
        if not token:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        return token
    except AppException as app_exc:
        return await app_exceptions_handler(None, app_exc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@auth_router.post("/refresh", response_model=LoginResponseDTO)
async def refresh_token(
    refresh_token: str = Header(), 
    auth_service: IAuthService = Depends(get_auth_service)
):
    try:
        token = await auth_service.refresh_tokens(refresh_token)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        return token
    except AppException as app_exc:
        return await app_exceptions_handler(None, app_exc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@auth_router.get("/me", response_model=UserPydantic)
async def read_users_me(
    current_user: UserSQLAlchemy = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)
):
    try:
        user_with_tokens = await UserSQLAlchemy.get_user_with_tokens(session, current_user.id)
        if not user_with_tokens:
            raise HTTPException(status_code=404, detail="User not found")
        return user_with_tokens
    except AppException as app_exc:
        return await app_exceptions_handler(None, app_exc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@auth_router.get("/verify-token", response_model=UserPydantic)
async def verify_token(
    access_token: str = Header(...), 
    auth_service: IAuthService = Depends(get_auth_service)
):
    try:
        user = await auth_service.get_token_user(access_token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired access token")
        return user
    except AppException as app_exc:
        return await app_exceptions_handler(None, app_exc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@auth_router.post("", status_code=status.HTTP_201_CREATED, response_model=RegisterUserResponseDTO)
async def register_user(
    data: RegisterUserRequestDTO,
    registration_service: IRegistrationService = Depends(get_registration_service)
): # this router accepts a post request from the registration service
    try:
        new_user = await registration_service.register_user(data)
        return RegisterUserResponseDTO(
            id=new_user.id,
            name=data.name,
            email=new_user.email,
            phone_number=data.phone_number
        )
    except AppException as app_exc:
        return await app_exceptions_handler(None, app_exc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

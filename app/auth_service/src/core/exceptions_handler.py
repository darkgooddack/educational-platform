from fastapi.responses import JSONResponse
from fastapi import Request
from .exceptions import (
    AppException, 
    UserAlreadyExistsException, 
    UserNotFoundException, 
    ExternalServiceException,
    UserFetchFailedException, 
    TokenGenerationException, 
    InvalidTokenException, 
    TokenExpiredException,
    DatabaseException,
    DependencyException,
    )

async def app_exceptions_handler(request: Request, exc: AppException):
    if isinstance(exc, UserAlreadyExistsException):
        return JSONResponse(status_code=400, content={"detail": exc.message})
    
    if isinstance(exc, UserNotFoundException):
        return JSONResponse(status_code=404, content={"detail": exc.message})
    
    if isinstance(exc, DatabaseException):
        return JSONResponse(status_code=500, content={"detail": exc.message})
    
    if isinstance(exc, DependencyException):
        return JSONResponse(status_code=500, content={"detail": exc.message})

    if isinstance(exc, ExternalServiceException):
        return JSONResponse(status_code=500, content={"detail": exc.message})
    
    if isinstance(exc, UserFetchFailedException):
        return JSONResponse(status_code=500, content={"detail": exc.message})
    
    if isinstance(exc, TokenGenerationException):
        return JSONResponse(status_code=500, content={"detail": exc.message})
    
    if isinstance(exc, InvalidTokenException):
        return JSONResponse(status_code=400, content={"detail": exc.message})
    
    if isinstance(exc, TokenExpiredException):
        return JSONResponse(status_code=400, content={"detail": exc.message})

    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
"""
Общий роутер для аутентификации

"""

from fastapi import APIRouter

from .endpoints import router as auth_router
from .oauth import router as oauth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(oauth_router)

__all__ = ["router"]

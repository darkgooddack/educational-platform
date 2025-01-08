from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.routers.router import v1 as reg

route = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)
route.include_router(reg)
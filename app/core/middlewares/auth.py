from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LastActivityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        from app.core.storages.redis.auth import AuthRedisStorage
        
        # Получаем токен из заголовка
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            # Обновляем время последней активности
            redis = AuthRedisStorage()
            await redis.update_last_activity(token)
            
        return await call_next(request)
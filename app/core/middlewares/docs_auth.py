"""
Middleware для защиты доступа к документации API.

Обеспечивает:
- Базовую HTTP аутентификацию для /docs и /redoc
- Проверку включения документации через config.docs_access
- Валидацию логина/пароля из конфига
"""

from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import config
import time

security = HTTPBasic(description="Credentials for API documentation access")


class DocsAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware для аутентификации доступа к документации API.

    Проверяет basic auth credentials для путей:
    - /docs (Swagger UI)
    - /redoc (ReDoc UI)
    - /openapi.json (OpenAPI схема)

    Raises:
        HTTPException:
            - 401 при неверных credentials
            - 403 если docs_access выключен
    """
    def __init__(self, app):
        super().__init__(app)
        self.auth_cache = {}
        
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            if not config.docs_access:
                raise HTTPException(status_code=403, detail="Docs disabled")
            
            # Проверяем кэш авторизации
            client_ip = request.client.host
            cached_auth = self.auth_cache.get(client_ip)
            current_time = time.time()
            
            if cached_auth and current_time - cached_auth['timestamp'] < 3600:  # 1 час
                return await call_next(request)
            
            # Получаем заголовок Authorization
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return Response(
                    status_code=401,
                    headers={"WWW-Authenticate": "Basic"},
                )

            try:
                auth: HTTPBasicCredentials = await security(request)
                if (auth.username == config.docs_username and 
                    auth.password == config.docs_password):
                    # Сохраняем успешную авторизацию в кэш
                    self.auth_cache[client_ip] = {
                        'timestamp': current_time
                    }
                    return await call_next(request)
                raise HTTPException(status_code=401)
            except HTTPException:
                return Response(
                    status_code=401,
                    headers={"WWW-Authenticate": "Basic"},
                )

        return await call_next(request)

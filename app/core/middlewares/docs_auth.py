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

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            if not config.docs_access:
                raise HTTPException(status_code=403, detail="Docs disabled")

            # Получаем заголовок Authorization
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                return Response(
                    status_code=401,
                    headers={"WWW-Authenticate": "Basic"},
                )

            try:
                auth: HTTPBasicCredentials = await security(request)
                if (
                    auth.username != config.docs_username
                    or auth.password != config.docs_password
                ):
                    raise HTTPException(status_code=401)
            except HTTPException:
                return Response(
                    status_code=401,
                    headers={"WWW-Authenticate": "Basic"},
                )

        return await call_next(request)

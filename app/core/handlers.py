from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
import pytz

from app.core.exceptions import BaseAPIException

moscow_tz = pytz.timezone("Europe/Moscow")

async def api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": exc.error_type,
            "extra": exc.extra,
            "timestamp": datetime.now(moscow_tz).isoformat()
        }
    )
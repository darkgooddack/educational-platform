from app.core.exceptions.base import BaseAPIException

class SchedulerError(BaseAPIException):
    """Базовая ошибка планировщика"""
    
    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            status_code=500,
            detail=f"Ошибка планировщика: {message}",
            error_type="scheduler_error",
            extra=extra
        )

class SessionCheckError(SchedulerError):
    """Ошибка проверки сессий"""
    
    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            message=f"Ошибка проверки сессий: {message}",
            extra=extra
        )

class StatusSyncError(SchedulerError):
    """Ошибка синхронизации статусов"""
    
    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            message=f"Ошибка синхронизации статусов: {message}", 
            extra=extra
        )
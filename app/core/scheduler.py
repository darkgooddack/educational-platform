import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.dependencies.database import SessionContextManager
from app.core.exceptions.v1.scheduler import SessionCheckError, StatusSyncError

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def check_sessions():
    try:
        from app.services.v1.auth.service import AuthService
        async with SessionContextManager() as session_manager:
            service = AuthService(session_manager.session)
            await service.check_expired_sessions()
            logger.info("Проверка сессий успешно завершена")
    except Exception as e:
        logger.error(f"Ошибка при проверке сессий: {str(e)}")
        raise SessionCheckError(str(e))

async def sync_statuses_to_db():
    try:
        from app.services.v1.auth.service import AuthService
        async with SessionContextManager() as session_manager:
            service = AuthService(session_manager.session)
            await service.sync_statuses_to_db()
            logger.info("Синхронизация статусов успешно завершена")
    except Exception as e:
        logger.error(f"Ошибка при синхронизации статусов: {str(e)}")
        raise StatusSyncError(str(e))

# Проверка сессий каждые 5 минут
scheduler.add_job(check_sessions, 'interval', minutes=5)

# Синхронизация с БД каждый час (is_online и last_seen) 
scheduler.add_job(sync_statuses_to_db, 'interval', minutes=60)
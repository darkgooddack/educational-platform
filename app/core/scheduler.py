import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.dependencies.database import SessionContextManager
from app.core.exceptions import SessionCheckError, StatusSyncError

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def check_and_schedule():
    redis_storage = AuthRedisStorage()
    active_tokens = await redis_storage.get_all_tokens()
    
    if active_tokens:
        if not scheduler.get_job('check_sessions'):
            # Проверка сессий каждые 5 минут
            scheduler.add_job(check_sessions, 'interval', minutes=5, id='check_sessions')
            # Синхронизация с БД каждый час (is_online и last_seen) 
            scheduler.add_job(sync_statuses_to_db, 'interval', minutes=60, id='sync_statuses')
            logger.info("Планировщик запущен - обнаружены активные пользователи")
    else:
        scheduler.remove_job('check_sessions')
        scheduler.remove_job('sync_statuses')
        logger.info("Планировщик остановлен - нет активных пользователей")


async def check_sessions():
    try:
        from app.services.v1.auth.service import AuthService
        from app.core.storages.redis.auth import AuthRedisStorage

        # Проверяем есть ли активные токены
        redis_storage = AuthRedisStorage()
        active_tokens = await redis_storage.get_all_tokens()
        
        if not active_tokens:
            logger.debug("Нет активных сессий для проверки")
            return

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
        from app.core.storages.redis.auth import AuthRedisStorage
        
        # Проверяем есть ли активные токены
        redis_storage = AuthRedisStorage()
        active_tokens = await redis_storage.get_all_tokens()
        
        if not active_tokens:
            logger.debug("Нет активных пользователей для синхронизации статусов")
            return

        async with SessionContextManager() as session_manager:
            service = AuthService(session_manager.session)
            await service.sync_statuses_to_db()
            logger.info("Синхронизация статусов успешно завершена")
    except Exception as e:
        logger.error(f"Ошибка при синхронизации статусов: {str(e)}")
        raise StatusSyncError(str(e))


# Проверяем каждую минуту наличие активных пользователей
scheduler.add_job(check_and_schedule, 'interval', minutes=1)
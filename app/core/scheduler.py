from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies.database import get_db_session

scheduler = AsyncIOScheduler()

async def check_sessions():
    from app.services.v1.auth.service import AuthService
    async for session in get_db_session():
        service = AuthService(session)
        await service.check_expired_sessions()

async def sync_statuses_to_db():
    from app.services.v1.auth.service import AuthService
    async for session in get_db_session():
        service = AuthService(session)
        await service.sync_statuses_to_db()

# Проверка сессий каждые 5 минут
scheduler.add_job(check_sessions, 'interval', minutes=5)

# Синхронизация с БД каждый час (is_online и last_seen) 
scheduler.add_job(sync_statuses_to_db, 'interval', minutes=60)
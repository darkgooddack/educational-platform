from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.v1.auth.service import AuthService

scheduler = AsyncIOScheduler()

async def check_sessions(session: AsyncSession):
    service = AuthService(session)
    await service.check_expired_sessions()

# Запускать каждые 5 минут
scheduler.add_job(check_sessions, 'interval', minutes=5)
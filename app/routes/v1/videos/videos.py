import logging
from fastapi import APIRouter, Depends, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, get_current_user, get_s3_session
from app.core.dependencies.s3 import S3Session
from app.schemas import VideoLectureResponseSchema, VideoLectureSchema, VideoLectureCreateSchema, UserCredentialsSchema, Page, PaginationParams
from app.services import VideoLectureService

logger = logging.getLogger(__name__)

def setup_routes(router: APIRouter):

    @router.post("/", response_model=VideoLectureResponseSchema)
    async def create_video_lecture(
        title: str = Form(...),
        description: str = Form(...),
        video_file: UploadFile = File(
            ...,
            description="Видео лекции",
            content_type=["video/mov", "video/quicktime", "video/mp4", "video/webm", "video/avi"],
            max_size=500_000_000,  # 500MB
        ),
        thumbnail_file: UploadFile = File(
            ...,
            description="Обложка видео лекции",
            content_type=["image/jpeg", "image/png", "image/gif"],
            max_size=10_000_000,  # 10MB
        ),
        _current_user: UserCredentialsSchema = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session),
        s3_session: S3Session = Depends(get_s3_session),
    ) -> VideoLectureResponseSchema:
        """
        **Добавление видео лекции.**

        **Args**:
            title (str): Заголовок видео лекции.
            description (str): Описание видео лекции.
            video_file (UploadFile): Файл видео лекции.
            thumbnail_file (UploadFile): Файл обложки видео лекции.
            _current_user (UserCredentialsSchema): Данные текущего пользователя.
            db_session (AsyncSession): Сессия базы данных.
            s3_session (S3Session): Сессия S3.

        **Returns**:
            VideoLectureResponseSchema: Созданный отзыв.
        """
        logger.debug("🎥 Начало обработки запроса на добавление видео лекции")
        logger.debug("📝 Параметры запроса: title='%s', description='%s'", title, description)
        logger.debug("📁 Видео файл лекции: filename='%s', content_type='%s', size=%d bytes",
                video_file.filename, video_file.content_type, video_file.size)
        logger.debug("📷 Обложка: filename='%s', content_type='%s', size=%d bytes")
        logger.debug("👤 Пользователь: id=%d, email='%s'",
                _current_user.id, _current_user.email)

        try:
            service = VideoLectureService(db_session, s3_session)
            result = await service.add_video(
                VideoLectureCreateSchema(
                    title=title,
                    description=description,
                    video_file=video_file,
                    thumbnail_file=thumbnail_file,
                ),
                author_id=_current_user.id
            )
            logger.debug("✅ Видео успешно загружено: %s", result)
            return result

        except Exception as e:
            logger.error("❌ Ошибка при загрузке видео: %s", str(e))
            raise

    @router.get("/", response_model=Page[VideoLectureSchema])
    async def get_videos(
        pagination: PaginationParams = Depends(),
        theme: str = None,
        search: str = None,
        db_session: AsyncSession = Depends(get_db_session),
    ) -> Page[VideoLectureSchema]:
        """
        **Получение видео лекций с пагинацией, фильтрацией и поиском.**

        **Args**:
            - pagination (PaginationParams): Параметры пагинации.
            - theme (str): Фильтр по тематике
            - search (str): Поиск по названию и описанию
            - db_session (AsyncSession): Сессия базы данных.
            - sort_by: Доступные значения (views, updated_at)

        **Returns**:
            - Page[VideoLectureSchema]: Страница с видео лекциями.
        """
        service = VideoLectureService(db_session)
        videos, total = await service.get_videos(
            pagination=pagination,
            theme=theme,
            search=search,
        )
        return Page(
            items=videos, total=total, page=pagination.page, size=pagination.limit
        )


__all__ = ["setup_routes"]

from fastapi import APIRouter, Depends, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, get_current_user, get_s3_session
from app.core.dependencies.s3 import S3Session
from app.schemas import VideoLectureResponseSchema, VideoLectureSchema, VideoLectureCreateSchema, UserSchema, Page, PaginationParams
from app.services import VideoLectureService


def setup_routes(router: APIRouter):

    @router.post("/")
    async def create_video_lecture(
        title: str = Form(...),
        description: str = Form(...),
        file: UploadFile = Form(...),
        _current_user: UserSchema = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session),
        s3_session: S3Session = Depends(get_s3_session),
    ) -> VideoLectureResponseSchema:
        """
        **Добавление видео лекции.**

        **Args**:
            video_lecture (VideoLectureCreateSchema): Данные видеолекции для создания.
            db_session (AsyncSession): Сессия базы данных.

        **Returns**:
            VideoLectureSchema: Созданный отзыв.
        """
        service = VideoLectureService(db_session, s3_session)
        result = await service.add_video(
            VideoLectureCreateSchema(
                title=title,
                description=description,
                video_file=file
            ),
            author_id=_current_user.id
        )
        return result

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

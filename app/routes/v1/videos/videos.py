import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (get_current_user, get_db_session,
                                   get_s3_session)
from app.core.dependencies.s3 import S3Session
from app.schemas import (PaginationParams, UserCredentialsSchema,
                         VideoLectureCreateSchema, VideoLectureCreateResponse,
                         VideoLectureListResponse)
from app.services import VideoLectureService

logger = logging.getLogger(__name__)


def setup_routes(router: APIRouter):

    @router.post("/", response_model=VideoLectureCreateResponse)
    async def create_video_lecture(
        title: str = Form(...),
        description: str = Form(...),
        theme_id: int = Form(..., description="ID темы"),
        video_file: UploadFile = File(
            ...,
            description="Видео лекции",
            content_type=[
                "video/mov",
                "video/quicktime",
                "video/mp4",
                "video/webm",
                "video/avi",
            ],
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
    ) -> VideoLectureCreateResponse:
        """
        **Добавление видео лекции.**

        **Args**:
            title (str): Заголовок видео лекции.
            description (str): Описание видео лекции.
            theme_id (int): ID темы видео лекции.
            video_file (UploadFile): Файл видео лекции.
            thumbnail_file (UploadFile): Файл обложки видео лекции.
            _current_user (UserCredentialsSchema): Данные текущего пользователя.
            db_session (AsyncSession): Сессия базы данных.
            s3_session (S3Session): Сессия S3.

        **Returns**:
            VideoLectureCreateResponse: Данные созданной видео лекции.
        """

        service = VideoLectureService(db_session, s3_session)
        result = await service.add_video(
            VideoLectureCreateSchema(
                title=title,
                description=description,
                theme_id=theme_id,
                video_file=video_file,
                thumbnail_file=thumbnail_file,
            ),
            author_id=_current_user.id,
        )

        return result

    @router.get("/", response_model=VideoLectureListResponse)
    async def get_videos(
        pagination: PaginationParams = Depends(),
        theme_id: Optional[int] = Query(None, description="Фильтр по тематике"),
        search: str = Query(None, description="Поиск по названию и описанию"),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> VideoLectureListResponse:
        """
        **Получение видео лекций с пагинацией, фильтрацией и поиском.**

        **Args**:
            - pagination (PaginationParams): Параметры пагинации.
            - theme_id (int): Фильтр по тематике
            - search (str): Поиск по названию и описанию
            - db_session (AsyncSession): Сессия базы данных.
            - sort_by: Доступные значения (views, updated_at)

        **Returns**:
            - VideoLectureListResponse: Страница с видео лекциями.
        """
        service = VideoLectureService(db_session)
        videos, total = await service.get_videos(
            pagination=pagination,
            theme_id=theme_id,
            search=search,
        )
        return VideoLectureListResponse(
            items=videos,
            total=total,
            page=pagination.page,
            size=pagination.limit
        )


__all__ = ["setup_routes"]

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies.s3 import S3Session
from app.core.storages.s3.base import S3DataManager
from app.services import BaseService
from app.schemas import  VideoLectureResponseSchema, VideoLectureSchema, VideoLectureCreateSchema, PaginationParams
from .data_manager import VideoLectureDataManager

class VideoLectureService(BaseService):
    """
    Сервис для управления c видео лекциями.

    Предоставляет высокоуровневые методы для работы с видео лекциями,
    инкапсулируя бизнес-логику и взаимодействие с базой данных.

    Attributes:
        session (AsyncSession): Асинхронная сессия для работы с БД
        _data_manager (VideoLectureDataManager): Менеджер для работы с данными видео лекций

    Methods:
        get_videos: Получает список видео лекций с возможностью пагинации, поиска и фильтрации.

    """
    def __init__(
        self,
        session: AsyncSession,
        s3_session: S3Session | None = None
    ):
        super().__init__()
        self.session = session
        self._data_manager = VideoLectureDataManager(session)
        self._s3_manager = S3DataManager(s3_session)

    async def add_video(
        self,
        video_lecture: VideoLectureCreateSchema,
        author_id: int
    ) -> VideoLectureResponseSchema:
        """
        Добавляет новую инструкцию.

        Args:
            video_lecture (VideoLectureCreateSchema): Видео лекция для добавления.
            author_id (int): Идентификатор автора.

        Returns:
            VideoLectureResponseSchema: Добавленная видеолекция с полученным URL-адресом файла.
        """
        video_url = await self._s3_manager.upload_file_from_content(
            file=video_lecture.video_file,
            file_key="videos_lectures"
        )

        thumbnail_url = await self._s3_manager.upload_file_from_content(
            file=video_lecture.thumbnail_file,
            file_key="thumbnails"
        )

        new_video_lecture = VideoLectureSchema(
            title=video_lecture.title,
            description=video_lecture.description,
            video_url=video_url,
            theme="default_theme",
            views=0,
            duration=0,
            author_id=author_id,
            thumbnail_url=thumbnail_url
        )
        await self._data_manager.add_item(new_video_lecture)
        return VideoLectureResponseSchema(
            user_id=author_id,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            message="Видео успешно добавлено"
        )

    async def get_videos(
        self,
        pagination: PaginationParams,
        theme: str = None,
        search: str = None,
    ) -> tuple[List[VideoLectureSchema], int]:
        """
        Получает список видео лекций с возможностью пагинации, поиска и фильтрации.

        Args:
            pagination (PaginationParams): Параметры пагинации.
            theme (str): Фильтр по тематике
            search (str): Поиск по названию и описанию
            sort_by: Доступные значения (views, updated_at)

        Returns:
            tuple[List[VideoLectureSchema], int]: Список с видео лекциями и общее количество.
        """
        return await self._data_manager.get_videos(
            pagination=pagination,
            theme=theme,
            search=search,
        )
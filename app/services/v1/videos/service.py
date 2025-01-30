from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import VideoLectureModel
from app.services import BaseService
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
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self._data_manager = VideoLectureDataManager(session, self.model)

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
            role=role,
            search=search,
        )
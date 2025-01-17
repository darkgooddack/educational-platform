"""
Сервис для кэширования данных в БД.

Предоставляет методы для работы с кэшем токенов и маршрутов.
Использует BaseService для выполнения CRUD операций.

Основные операции:
    - Кэширование токенов
    - Получение токенов из кэша
    - Кэширование маршрутов
    - Получение маршрутов из кэша
"""

from app.models import RouteCacheModel, TokenCacheModel
from app.schemas import RouteCacheSchema, TokenCacheSchema
from app.services import BaseService


class CacheService:
    """
    Сервис для работы с кэшем в БД.

    Attributes:
        token_service (BaseService): Сервис для работы с токенами
        route_service (BaseService): Сервис для работы с маршрутами
    """

    def __init__(self, session):
        self.token_service = BaseService(session, TokenCacheSchema, TokenCacheModel)
        self.route_service = BaseService(session, RouteCacheSchema, RouteCacheModel)

    async def cache_token(self, data: dict):
        """
        Кэширует токен в БД.

        Args:
            data (dict): Данные токена для кэширования

        Returns:
            TokenCacheSchema: Сериализованный объект токена
        """
        return await self.token_service.create(data)

    async def get_token(self, token: str):
        """
        Получает токен из кэша.

        Args:
            token (str): Значение токена для поиска

        Returns:
            TokenCacheSchema | None: Найденный токен или None
        """
        return await self.token_service.get(token=token)

    async def cache_route(self, data: dict):
        """
        Кэширует маршрут в БД.

        Args:
            data (dict): Данные маршрута для кэширования

        Returns:
            RouteCacheSchema: Сериализованный объект маршрута
        """
        return await self.route_service.create(data)

    async def get_route(self, path: str):
        """
        Получает маршрут из кэша.

        Args:
            path (str): Путь маршрута для поиска

        Returns:
            RouteCacheSchema | None: Найденный маршрут или None
        """
        return await self.route_service.get(path=path)

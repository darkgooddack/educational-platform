"""
Модели для кэширования в API Gateway.

Содержит:
- TokenCacheModel: кэширование JWT токенов
- RouteCacheModel: кэширование маршрутов к микросервисам
"""
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.models import BaseModel

class TokenCacheModel(BaseModel):
    """
    Модель кэширования JWT токенов.

    Attributes:
        token (str): JWT токен (primary key)
        user_id (str): ID пользователя
        expires_at (datetime): Время истечения токена
    """
    __tablename__ = "token_cache"

    token: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)

class RouteCacheModel(BaseModel):
    """
    Модель кэширования маршрутов к микросервисам.

    Attributes:
        path (str): URL путь запроса (primary key)
        service (str): Название целевого микросервиса
        method (str): HTTP метод (GET, POST и т.д.)
    """
    __tablename__ = "route_cache"

    path: Mapped[str] = mapped_column(primary_key=True)
    service: Mapped[str] = mapped_column(nullable=False)
    method: Mapped[str] = mapped_column(nullable=False)
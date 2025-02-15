"""
Классы исключений для модуля тем.

Этот модуль содержит классы исключений,
которые могут быть вызваны при работе с темами.

Включают в себя:
- ThemeNotFoundError: Исключение при отсутствии темы
- ThemeExistsError: Исключение при попытке создать существующую тему
"""

from app.core.exceptions.v1.base import BaseAPIException, DatabaseError


class ThemeNotFoundError(BaseAPIException):
    """
    Тема не найдена.

    Attributes:
        message (str): Сообщение об ошибке
        theme_id (int): ID темы, которая не найдена
    """

    def __init__(self, message: str, theme_id: int = None):
        super().__init__(
            status_code=404,
            detail=message,
            error_type="theme_not_found",
            extra={"theme_id": theme_id} if theme_id else None,
        )


class ThemeExistsError(BaseAPIException):
    """
    Тема уже существует.

    Attributes:
        name (str): Название темы, которая уже существует
    """

    def __init__(self, name: str):
        super().__init__(
            status_code=409,
            detail=f"Тема с названием '{name}' уже существует",
            error_type="theme_exists",
            extra={"theme_name": name},
        )

class ThemeUpdateError(DatabaseError):
    """
    Ошибка при обновлении темы в базе данных.
    """

    def __init__(self, message: str, extra: dict = None):
        super().__init__(message=f"Ошибка при обновлении темы: {message}", extra=extra)

class ThemeDeleteError(DatabaseError):
    """
    Ошибка при удалении темы из базы данных.

    Attributes:
        message (str): Сообщение об ошибке.
    """

    def __init__(self, message: str, extra: dict = None):
        super().__init__(message=f"Ошибка при удалении темы: {message}", extra=extra)
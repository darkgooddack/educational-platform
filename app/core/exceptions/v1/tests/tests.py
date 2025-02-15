"""
Классы исключений для модуля тестов.

Этот модуль содержит классы исключений,
которые могут быть вызваны при работе с тестами.

Включают в себя:
- TestGetError: Исключение при отсутствии теста
- TestExistsError: Исключение при попытке создать существующий тест
- QuestionNotFoundError: Исключение при отсутствии вопроса
"""

from app.core.exceptions.v1.base import BaseAPIException, DatabaseError


class TestGetError(DatabaseError):
    """
    Ошибка при получении теста из базы данных.

    Attributes:
        message (str): Сообщение об ошибке.
    """

    def __init__(self, message: str, extra: dict = None):
        super().__init__(message=f"Ошибка при получении теста: {message}", extra=extra)


class TestExistsError(BaseAPIException):
    """
    Тест уже существует.

    Attributes:
        title (str): Название теста, который уже существует
    """

    def __init__(self, title: str):
        super().__init__(
            status_code=409,
            detail=f"Тест с названием '{title}' уже существует",
            error_type="test_exists",
            extra={"test_title": title},
        )


class QuestionNotFoundError(BaseAPIException):
    """
    Вопрос не найден.

    Attributes:
        message (str): Сообщение об ошибке
        question_id (int): ID вопроса, который не найден
    """

    def __init__(self, message: str, question_id: int = None):
        super().__init__(
            status_code=404,
            detail=message,
            error_type="question_not_found",
            extra={"question_id": question_id} if question_id else None,
        )


class TestUpdateError(DatabaseError):
    """
    Ошибка при обновлении теста в базе данных.
    """

    def __init__(self, message: str, extra: dict = None):
        super().__init__(message=f"Ошибка при обновлении теста: {message}", extra=extra)


class TestDeleteError(DatabaseError):
    """
    Ошибка при удалении теста из базы данных.

    Attributes:
        message (str): Сообщение об ошибке.
    """

    def __init__(self, message: str, extra: dict = None):
        super().__init__(message=f"Ошибка при удалении теста: {message}", extra=extra)

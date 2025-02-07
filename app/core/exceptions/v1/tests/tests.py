"""
Классы исключений для модуля тестов.

Этот модуль содержит классы исключений,
которые могут быть вызваны при работе с тестами.

Включают в себя:
- TestNotFoundError: Исключение при отсутствии теста
- TestExistsError: Исключение при попытке создать существующий тест
- QuestionNotFoundError: Исключение при отсутствии вопроса
"""

from app.core.exceptions.v1.base import BaseAPIException


class TestNotFoundError(BaseAPIException):
    """
    Тест не найден.

    Attributes:
        message (str): Сообщение об ошибке
        test_id (int): ID теста, который не найден
    """

    def __init__(self, message: str, test_id: int = None):
        super().__init__(
            status_code=404,
            detail=message,
            error_type="test_not_found",
            extra={"test_id": test_id} if test_id else None
        )


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
            extra={"test_title": title}
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
            extra={"question_id": question_id} if question_id else None
        )

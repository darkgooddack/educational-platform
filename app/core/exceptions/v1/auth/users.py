"""
Классы исключений для модуля users.

Этот модуль содержит классы исключений,
которые могут быть вызваны при работе с пользователями.

Включают в себя:
- UserNotFoundError: Исключение, которое вызывается, когда пользователь не найден.
- UserExistsError: Исключение, которое вызывается, когда пользователь с таким именем или email уже существует.
"""

from app.core.exceptions.v1.base import BaseAPIException


class UserNotFoundError(BaseAPIException):
    """
    Пользователь не найден.

    Attributes:
        field (str): Поле, по которому не найден пользователь.
        value (str): Значение поля, по которому не найден пользователь.
    """

    def __init__(self, field: str, value: str):

        match field:
            case "email":
                field = "email"
            case "name":
                field = "именем"
            case "phone":
                field = "телефоном"
            case _:
                field = field

        super().__init__(
            status_code=404,
            detail=f"Пользователь с {field} '{value}' не существует!",
            error_type="user_not_found",
            extra={"user_" + field: value},
        )


class UserExistsError(BaseAPIException):
    """
    Пользователь с таким именем существует.

    Attributes:
        field (str): Поле, по которому существует пользователь.
        value (str): Значение поля, по которому существует пользователь.
    """

    def __init__(self, field: str, value: str):

        match field:
            case "email":
                field = "email"
            case "name":
                field = "именем"
            case "phone":
                field = "телефоном"
            case _:
                field = field

        super().__init__(
            status_code=400,
            detail=f"Пользователь с {field} '{value}' существует",
            error_type="user_exists",
            extra={"user_" + field: value},
        )


class UserCreationError(BaseAPIException):
    """
    Ошибка при создании пользователя.

    Attributes:
        detail (str): Подробности об ошибке.
    """

    def __init__(self, detail: str):
        super().__init__(
            status_code=500, detail=detail, error_type="user_creation_error", extra={}
        )

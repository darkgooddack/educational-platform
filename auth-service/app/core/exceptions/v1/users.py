"""
Классы исключений для модуля users.

Этот модуль содержит классы исключений,
которые могут быть вызваны при работе с пользователями.

Включают в себя:

- InvalidEmailFormatError: Исключение, которое вызывается, когда формат email недействителен.
- WeakPasswordError: Исключение, которое вызывается, когда пароль является слабым.
- UserNotFoundError: Исключение, которое вызывается, когда пользователь не найден.
- UserExistsError: Исключение, которое вызывается, когда пользователь с таким именем или email уже существует.
"""

from .base import BaseAPIException


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


class InvalidEmailFormatError(BaseAPIException):
    """
    Исключение, которое вызывается, когда формат email недействителен.

    Attributes:
        email (str): Недействительный email.
    """

    def __init__(self, email: str):
        super().__init__(
            status_code=400,
            detail=f"Неверный формат email: {email}",
            error_type="invalid_email_format",
            extra={"email": email},
        )


class WeakPasswordError(BaseAPIException):
    """
    Исключение, которое вызывается, когда пароль является слабым.

    Attributes:
        password (str): Слабый пароль.
    """

    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Пароль должен быть минимум 4 символов!",
            error_type="weak_password",
            extra={},
        )

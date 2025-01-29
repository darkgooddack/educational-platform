from app.core.exceptions.v1.base import DatabaseError


class FeedbackAddError(DatabaseError):
    """
    Ошибка при добавлении обратной связи в базу данных.

    Attributes:
        message (str): Сообщение об ошибке.
    """

    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            message=f"Ошибка при добавлении обратной связи: {message}", extra=extra
        )

class FeedbackDeleteError(DatabaseError):
    """
    Ошибка при удалении обратной связи из базы данных.

    Attributes:
        message (str): Сообщение об ошибке.
    """

    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            message=f"Ошибка при удалении обратной связи: {message}",
            extra=extra
        )

class FeedbackGetError(DatabaseError):
    """
    Ошибка при получении обратной связи из базы данных.

    Attributes:
        message (str): Сообщение об ошибке.
    """

    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            message=f"Ошибка при получении обратной связи: {message}",
            extra=extra
        )

class FeedbackUpdateError(DatabaseError):
    """
    Ошибка при обновлении обратной связи в базе данных.

    Attributes:
        message (str): Сообщение об ошибке.
    """
    def __init__(self, message: str, extra: dict = None):
        super().__init__(
            message=f"Ошибка при обновлении обратной связи: {message}",
            extra=extra
        )

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

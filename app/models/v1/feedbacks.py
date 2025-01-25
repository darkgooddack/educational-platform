from sqlalchemy.orm import Mapped, mapped_column
from app.models import BaseModel

class FeedbackModel(BaseModel):
    """
    Модель для представления обратной связи от пользователей.

    Attributes:
        name (str): Имя пользователя.
        phone (str): Номер телефона пользователя.
        email (str): Электронная почта пользователя.
        consent (bool): Согласие на обработку персональных данных.
    """

    __tablename__ = "feedback"

    name: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=False)
    consent: Mapped[bool] = mapped_column(default=False, nullable=False)

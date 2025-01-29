from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import BaseModel
from app.models.v1 import TYPE_CHECKING
from app.schemas import FeedbackStatus

if TYPE_CHECKING:
    from app.models.v1.users import UserModel


class FeedbackModel(BaseModel):
    """
    Модель для представления обратной связи от пользователей.

    Attributes:
        name (str): Имя пользователя.
        phone (str): Номер телефона пользователя.
        email (str): Электронная почта пользователя.
        status (FeedbackStatus): Статус обратной связи. (по умолчанию PENDING)
        manager_id (int): ID менеджера, который обрабатывает обратную связь.

    Relationships:
        manager (UserModel): Менеджер, который обрабатывает обратную связь.
    """

    __tablename__ = "feedback"

    name: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[FeedbackStatus] = mapped_column(
        default=FeedbackStatus.PENDING, nullable=False
    )
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    manager: Mapped["UserModel"] = relationship("UserModel", back_populates="feedbacks")

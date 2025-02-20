from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.schemas import MessageRole, ModelType, ModelVersion
from app.models import BaseModel
from app.models.v1 import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.v1.users import UserModel

class ChatModel(BaseModel):
    pass
    """
    Модель для хранения чатов

    Attributes:
        user_id (int): ID пользователя, создавшего чат
        title (str): Заголовок чата
        messages (list[MessageModel]): Сообщения в чате

    Relationships:
        user (UserModel): Пользователь, создавший чат
        messages (list[MessageModel]): Сообщения в чате
    """
    __tablename__ = "aichat_chats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="chats")
    messages: Mapped[list["MessageModel"]] = relationship(back_populates="chat", cascade="all, delete-orphan")

class MessageModel(BaseModel):
    """
    Модель для хранения сообщений в чате

    Attributes:
        chat_id (int): ID чата
        role (MessageRole): Роль сообщения
        content (str): Содержание сообщения

    Relationships:
        chat (ChatModel): Чат, к которому относится сообщение
    """
    __tablename__ = "aichat_messages"

    chat_id: Mapped[int] = mapped_column(ForeignKey("aichat_chats.id"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(default=MessageRole.USER)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    chat: Mapped["ChatModel"] = relationship("ChatModel", back_populates="messages")


class UsageModel(BaseModel):
    """
    Модель для учета использования AI.

    Attributes:
        user_id (int): ID пользователя
        input_tokens (int): Количество входных токенов
        completion_tokens (int): Количество токенов в ответе
        total_tokens (int): Общее количество токенов
        cost (float): Стоимость в рублях
        model_type (str): Тип модели (YandexGPT Lite/Pro)
        is_async (bool): Асинхронный режим

    Relationships:
        user (UserModel): Пользователь
    """

    __tablename__ = "aichat_usage"

    chat_id: Mapped[int] = mapped_column(ForeignKey("aichat_chats.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    model_type: Mapped[ModelType] = mapped_column(default=ModelType.YANDEX_GPT_PRO)
    model_version: Mapped[ModelVersion] = mapped_column(default=ModelVersion.LATEST)
    input_tokens: Mapped[int] = mapped_column(nullable=False)
    completion_tokens: Mapped[int] = mapped_column(nullable=False)
    total_tokens: Mapped[int] = mapped_column(nullable=False)
    cost: Mapped[float] = mapped_column(nullable=False)
    is_async: Mapped[bool] = mapped_column(default=False)

    chat: Mapped["ChatModel"] = relationship("ChatModel")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="aichat_usage")

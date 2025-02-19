
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import Message, MessageRole, AIChatResponse, AIChatRequest, CompletionOptions
from app.services.v1.base import BaseService
from app.core.http.aichat import AIChatHttpClient

from app.core.config import config

logger = logging.getLogger(__name__)

class AIChatService(BaseService):
    """
    Сервис для работы с чатом с AI

    Attributes:
        session: Сессия базы данных
        http_client: HTTP клиент для работы с AI API
    """
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.http_client = AIChatHttpClient()

    SYSTEM_MESSAGE = Message(role="system", text="Ты умный ассистент, который помогает пользователям")
    async def get_completion(self, message: str, role: MessageRole) -> AIChatResponse:
        """
        Получает ответ от модели на основе истории сообщений

        Args:
            request: Запрос к AI модели

        Returns:
            AIChatResponse: Ответ от модели
        """

        full_request = AIChatRequest(
            modelUri=config.yandex_model_uri,
            completionOptions=CompletionOptions(),
            messages=[
                self.SYSTEM_MESSAGE,
                Message(role=role, text=message)
            ]
        )

        async with self.http_client as client:
            return await client.get_completion(full_request)

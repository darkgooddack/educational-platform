
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
        self.message_history = []
        self.max_history = 100  # Максимальное количество сообщений в истории
        self.max_tokens = 4000  # Максимальное количество токенов в сообщении

    SYSTEM_MESSAGE = Message(role="system", text="Ты умный ассистент, который помогает пользователям")

    def _add_to_history(self, message: Message):
        self.message_history.append(message)
        # Удаляем старые сообщения если превышен лимит
        while len(self.message_history) > self.max_history:
            self.message_history.pop(0)

    def _clear_history(self):
        """Очистка истории"""
        self.message_history.clear()

    async def get_completion(self, message: str, role: MessageRole = MessageRole.USER) -> AIChatResponse:
        """
        Получает ответ от модели на основе истории сообщений

        Args:
            request: Запрос к AI модели

        Returns:
            AIChatResponse: Ответ от модели
        """
        try:
            # Создаем новое сообщение
            new_message = Message(role=role, text=message)

            # Добавляем в историю сообщения user и ассистента
            self._add_to_history(new_message)

            # Формируем полный список сообщений
            messages = [self.SYSTEM_MESSAGE] + self.message_history

            full_request = AIChatRequest(
                modelUri=config.yandex_model_uri,
                completionOptions=CompletionOptions(maxTokens=str(self.max_tokens)),
                messages=messages
            )

            async with self.http_client as client:
                response = await client.get_completion(full_request)

                # Добавляем ответ ассистента в историю
                if response.success:
                    assistant_message = Message(
                        role=MessageRole.ASSISTANT,
                        text=response.result.alternatives[0].message.text
                    )
                    self._add_to_history(assistant_message)

                return response
        except Exception as e:
            logger.error(f"Error in get_completion: {e}")
            self._clear_history()  # Очищаем историю при ошибке
            raise
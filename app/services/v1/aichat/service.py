import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.http.aichat import AIChatHttpClient
from app.core.storages.redis.aichat import AIChatRedisStorage
from app.schemas import (AIChatRequest, AIChatResponse, CompletionOptions,
                         Message, MessageRole)
from app.services.v1.base import BaseService

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
        self.storage = AIChatRedisStorage()
        self.max_tokens = 4000  # Максимальное количество токенов в сообщении

    SYSTEM_MESSAGE = Message(
        role="system", text="Ты умный ассистент, который помогает пользователям"
    )

    async def get_completion(
        self, message: str, user_id: int, role: MessageRole = MessageRole.USER
    ) -> AIChatResponse:
        """
        Получает ответ от модели на основе истории сообщений

        Args:
            request: Запрос к AI модели

        Returns:
            AIChatResponse: Ответ от модели
        """
        try:
            # Получаем историю
            message_history = await self.storage.get_chat_history(user_id)

            # Создаем новое сообщение
            new_message = Message(role=role, text=message)

            # Добавляем новое сообщение в историю
            message_history.append(new_message)

            # Формируем полный список сообщений
            messages = [self.SYSTEM_MESSAGE] + message_history

            request = AIChatRequest(
                modelUri=config.yandex_model_uri,
                completionOptions=CompletionOptions(maxTokens=str(self.max_tokens)),
                messages=messages,
            )

            async with self.http_client as client:
                response = await client.get_completion(request)

                # Добавляем ответ ассистента в историю
                if response.success:
                    assistant_message = Message(
                        role=MessageRole.ASSISTANT,
                        text=response.result.alternatives[0].message.text,
                    )
                    message_history.append(assistant_message)

                    # Сохраняем обновленную историю
                    await self.storage.save_chat_history(user_id, message_history)

                return response
        except Exception as e:
            logger.error(f"Error in get_completion: {e}")
            await self.storage.clear_chat_history(user_id)
            raise

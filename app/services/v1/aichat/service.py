import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.http.aichat import AIChatHttpClient
from app.core.storages.redis.aichat import AIChatRedisStorage
from app.schemas import (AIChatRequest, AIChatResponse, CompletionOptions,
                         Message, MessageRole, ModelPricing)
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
        self.max_tokens = config.yandex_max_tokens

    SYSTEM_MESSAGE = Message(role=MessageRole.SYSTEM.value, text=config.pre_instruction)

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

    async def get_completion_async(
        self, message: str, user_id: int, role: MessageRole = MessageRole.USER
    ) -> AIChatResponse:
        """
        Асинхронное получение ответа от модели
        """
        try:
            message_history = await self.storage.get_chat_history(user_id)
            new_message = Message(role=role, text=message)
            message_history.append(new_message)
            messages = [self.SYSTEM_MESSAGE] + message_history

            request = AIChatRequest(
                modelUri=config.yandex_model_uri,
                completionOptions=CompletionOptions(maxTokens=str(self.max_tokens)),
                messages=messages,
            )

            async with self.http_client as client:
                # Получаем ID операции
                operation_id = await client.get_completion_async(request)

                # Ждем результат
                response = await client.get_operation_result(operation_id)

                if response.success:
                    assistant_message = Message(
                        role=MessageRole.ASSISTANT,
                        text=response.result.alternatives[0].message.text,
                    )
                    message_history.append(assistant_message)
                    await self.storage.save_chat_history(user_id, message_history)

                return response

        except Exception as e:
            logger.error(f"Error in get_completion_async: {e}")
            await self.storage.clear_chat_history(user_id)
            raise


@dataclass
class PricingCalculator:
    """
    Калькулятор стоимости использования моделей

    Usage:
    calculator = PricingCalculator()
    cost = calculator.calculate_cost(
        tokens=1000,
        model=calculator.get_model_pricing("yandexgpt-lite", is_async=True)
    )
    print(f"Стоимость: {cost} ₽") # 0.10₽
    """

    def calculate_cost(self, tokens: int, model: ModelPricing) -> float:
        units, price_per_1k = model.value
        return (tokens / 1000) * price_per_1k

    def get_model_pricing(self, model_type: str, is_async: bool) -> ModelPricing:
        pricing_map = {
            ("yandexgpt-lite", False): ModelPricing.YANDEX_GPT_LITE_SYNC,
            ("yandexgpt-lite", True): ModelPricing.YANDEX_GPT_LITE_ASYNC,
            ("yandexgpt", False): ModelPricing.YANDEX_GPT_PRO_SYNC,
            ("yandexgpt", True): ModelPricing.YANDEX_GPT_PRO_ASYNC,
            ("llama-lite", False): ModelPricing.LLAMA_8B_SYNC,
            ("llama-lite", True): ModelPricing.LLAMA_8B_ASYNC,
            ("llama", False): ModelPricing.LLAMA_70B_SYNC,
            ("llama", True): ModelPricing.LLAMA_70B_ASYNC,
        }
        return pricing_map.get(
            (model_type, is_async), ModelPricing.YANDEX_GPT_LITE_SYNC
        )

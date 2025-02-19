
from app.schemas import AIChatRequest, AIChatResponse
from app.core.exceptions import AIChatAuthError, AIChatCompletionError
from app.core.config import config
from .base import BaseHttpClient

class AIChatHttpClient(BaseHttpClient):
    """
    Класс для работы с API Yandex
    """

    async def get_completion(self, chat_request: AIChatRequest) -> AIChatResponse:
        """
        Получение ответа от Yandex API

        Args:
            chat_request: Запрос к API

        Returns:
            AIChatResponse: Ответ от API

        Raises:
            HTTPException: При ошибках запроса
        """
        headers = {
            "Authorization": f"Api-Key {config.yandex_api_key.get_secret_value()}",
            "Content-Type": "application/json"
        }

        if not config.yandex_api_key:
            raise AIChatAuthError("API ключ не задан")

        chat_request.modelUri = config.yandex_model_uri

        try:
            response = await self.post(
                url=config.yandex_api_url,
                headers=headers,
                data=chat_request.model_dump()
            )

            return AIChatResponse(**response)

        except Exception as e:
            self.logger.error("Ошибка при запросе к API Yandex: %s", str(e))
            raise AIChatCompletionError(str(e))

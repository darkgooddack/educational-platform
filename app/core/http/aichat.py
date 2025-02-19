
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
            "Authorization": f"Api-Key {config.api_key}",
            "Content-Type": "application/json"
        }

        if not config.api_key:
            raise AIChatAuthError("API ключ не задан")

        chat_request.modelUri = config.model_uri

        try:
            response = await self.post(
                url=config.base_url,
                headers=headers,
                data=chat_request.model_dump()
            )

            return AIChatResponse(
                text=response["result"]["alternatives"][0]["message"]["text"],
                status="success",
                success=True
            )
        except Exception as e:
            self.logger.error("Ошибка при запросе к API Yandex: %s", str(e))
            raise AIChatCompletionError(str(e))
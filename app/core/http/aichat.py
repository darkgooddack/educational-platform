
import json
from app.schemas import AIChatRequest, AIChatResponse, Result
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
            request_data = chat_request.model_dump(by_alias=True)
            for msg in request_data["messages"]:
                msg["role"] = msg["role"].value

            self.logger.debug("Request data: %s", request_data)

            response = await self.post(
                url=config.yandex_api_url,
                headers=headers,
                data=request_data
            )

            self.logger.debug("Raw response from API: %s", response)

            # Всегда парсим ответ как JSON
            # response = json.loads(raw_response) if isinstance(raw_response, str) else raw_response

            # self.logger.debug("Parsed response: %s", response)

            # if isinstance(response, str):
            #     response = json.loads(response)

            if not isinstance(response, dict):
                raise AIChatCompletionError("Невалидный ответ от API")

            if "error" in response:
                raise AIChatCompletionError(response["error"])

            result_data = response.get("result", {})

            if not all(key in result_data for key in ["alternatives", "usage", "modelVersion"]):
                self.logger.error("Invalid response structure: %s", response)
                raise AIChatCompletionError("Неверная структура ответа от API")

            # result_data = {
            #     "alternatives": response.get("alternatives", []),
            #     "usage": response.get("usage", {}),
            #     "modelVersion": response.get("modelVersion", "unknown")
            # }

            return AIChatResponse(
                success=True,
                result=Result(**result_data)
            )

        except Exception as e:
            self.logger.error("Ошибка при запросе к API Yandex: %s", str(e))
            raise AIChatCompletionError(str(e))

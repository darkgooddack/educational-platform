from app.core.config import config
from app.core.security import TokenMixin
from app.core.exceptions import AIChatAuthError, AIChatCompletionError
from app.schemas import AIChatRequest, AIChatResponse, Result

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
            "Content-Type": "application/json",
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
                url=config.yandex_api_url, headers=headers, data=request_data
            )

            self.logger.debug("Raw response from API: %s", response)

            if not isinstance(response, dict):
                raise AIChatCompletionError("Невалидный ответ от API")

            if "error" in response:
                raise AIChatCompletionError(response["error"])

            result_data = response.get("result", {})

            if not all(
                key in result_data for key in ["alternatives", "usage", "modelVersion"]
            ):
                self.logger.error("Invalid response structure: %s", response)
                raise AIChatCompletionError("Неверная структура ответа от API")

            return AIChatResponse(success=True, result=Result(**result_data))

        except Exception as e:
            self.logger.error("Ошибка при запросе к API Yandex: %s", str(e))
            raise AIChatCompletionError(str(e))

    async def get_completion_async(self, chat_request: AIChatRequest) -> str:
        """
        Получение ответа от Yandex API асинхронно
        (https://yandex.cloud/ru/docs/foundation-models/operations/yandexgpt/async-request#curl_2)

        Args:
            chat_request: Запрос к API

        Returns:
                AIChatResponse: Ответ от API
            Raises:
                HTTPException: При ошибках запроса
        """
        jwt_token = TokenMixin.get_iam_token(
            config.yandex_private_key.get_secret_value(),
            config.yandex_key_id
        )
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "x-folder-id": config.yandex_folder_id,
        }
        self.logger.debug("Отправляем асинхронный запрос с данными: %s", chat_request.model_dump())
        self.logger.debug("Заголовки запроса: %s", headers)
        response = await self.post(
            url="https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync",
            headers=headers,
            data=chat_request.model_dump(),
        )
        self.logger.debug("Получен ответ от API: %s", response)
        operation_id = response.get("id")
        if not operation_id:
            self.logger.error("ID операции отсутствует в ответе: %s", response)
            raise ValueError("Не получен ID операции")
        self.logger.debug("ID операции: %s", operation_id)
        # Второй запрос - получаем результат по operation_id
        result = await self.get(
            url=f"https://operation.api.cloud.yandex.net/operations/{operation_id}",
            headers={"Authorization": f"Bearer {config.yandex_api_key}"}
        )

        return result

    async def get_operation_result(self, operation_id: str) -> AIChatResponse:
        """
        Получение результата операции (используется с асинхронным запросом)

        Args:
            operation_id: ID операции

        Returns:
            AIChatResponse: Ответ от API
        """
        headers = {"Authorization": f"Bearer {config.yandex_api_key}"}
        response = await self.get(
            url=f"https://operation.api.cloud.yandex.net/operations/{operation_id}",
            headers=headers,
        )
        return AIChatResponse.model_validate(response["response"])

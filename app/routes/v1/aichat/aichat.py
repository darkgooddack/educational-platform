from fastapi import APIRouter, Depends, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.schemas import AIChatResponse, UserCredentialsSchema
from app.services import AIChatService


def setup_routes(router: APIRouter):

    @router.post("/completion", response_model=AIChatResponse)
    async def get_aichat_completion(
        message: str = Form(...),
        async_mode: bool = Query(False, description="Использовать асинхронный режим"),
        current_user: UserCredentialsSchema = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_db_session),
    ):
        """
        # Получение ответа от YandexGPT

        ## Args
        * **message** - Текст сообщения пользователя
        * **async_mode** - Использовать асинхронный режим (дешевле в 2 раза)
        * **current_user** - Данные текущего пользователя
        * **db_session** - Сессия базы данных

        ## Returns
        * **AIChatResponse** - Ответ от модели:
            * **success** - Признак успеха
            * **result** - Результат генерации:
                * **alternatives** - Варианты ответа
                * **usage** - Статистика использования токенов
                * **modelVersion** - Версия модели

        ## Пример ответа
        ```json
        {
            "success": true,
            "result": {
                "alternatives": [{
                    "message": {
                        "role": "assistant",
                        "text": "Ответ на ваш вопрос..."
                    },
                    "status": "ALTERNATIVE_STATUS_FINAL"
                }],
                "usage": {
                    "inputTextTokens": "19",
                    "completionTokens": "6",
                    "totalTokens": "25"
                },
                "modelVersion": "23.10.2024"
            }
        }
        ```
        """
        aichat_service = AIChatService(db_session)
        if async_mode:
            return await aichat_service.get_completion_async(message, current_user.id)
        return await aichat_service.get_completion(message, current_user.id)


__all__ = ["setup_routes"]

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session
from app.schemas import MessageRole, AIChatResponse
from app.services import AIChatService

def setup_routes(router: APIRouter):

    @router.post("/completion", response_model=AIChatResponse)
    async def get_aichat_completion(
        message: str = Form(...),
        db_session: AsyncSession = Depends(get_db_session),
    ):
        """
        # Получение ответа от AI модели

        ## Args
        * **request** - Запрос к AI модели с параметрами:
            * **stream** - Потоковая генерация (true/false)
            * **temperature** - Креативность ответов (0.0-1.0)
            * **maxTokens** - Ограничение длины ответа
            * **messages** - Массив сообщений:
                * **role** - Роль (user/system/assistant)
                * **text** - Текст сообщения
        * **db_session** - Сессия базы данных

        ## Returns
        * **AIChatResponse** - Ответ от модели:
            * **text** - Сгенерированный текст
            * **status** - Статус выполнения
            * **success** - Признак успеха

        ## Пример запроса
        ```json
        {
            "messages": [
                {
                    "role": "system",
                    "text": "Ты умный ассистент"
                },
                {
                    "role": "user",
                    "text": "Привет! Какими науками занимался Альберт Эйнштейн?"
                }
            ]
        }
        ```
        """
        aichat_service = AIChatService(db_session)
        return await aichat_service.get_completion(message)

__all__ = ["setup_routes"]
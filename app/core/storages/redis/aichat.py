import json
from typing import List
from app.core.storages.redis.base import BaseRedisStorage
from app.schemas import Message

class AIChatRedisStorage(BaseRedisStorage):
    """
    Redis хранилище для истории чата с AI
    """

    async def save_chat_history(self, user_id: int, messages: List[Message]) -> None:
        """
        Сохраняет историю чата пользователя
        """
        key = f"chat_history:{user_id}"
        messages_json = json.dumps([msg.model_dump() for msg in messages])
        await self.set(key, messages_json, expires=3600)  # Храним 1 час

    async def get_chat_history(self, user_id: int) -> List[Message]:
        """
        Получает историю чата пользователя
        """
        key = f"chat_history:{user_id}"
        history = await self.get(key)
        if not history:
            return []
        messages_data = json.loads(history)
        return [Message.model_validate(msg) for msg in messages_data]

    async def clear_chat_history(self, user_id: int) -> None:
        """
        Очищает историю чата пользователя
        """
        key = f"chat_history:{user_id}"
        await self.delete(key)

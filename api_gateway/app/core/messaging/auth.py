from enum import Enum
from typing import Tuple, Optional
from .base import MessageProducer

class AuthAction(Enum):
    AUTHENTICATE = "authenticate"
    OAUTH_AUTHENTICATE = "oauth_authenticate"
    LOGOUT = "logout"
    REGISTER = "register"

class AuthMessageProducer(MessageProducer):
    """
    Класс для отправки сообщений в RabbitMQ для аутентификации.
    
    Attributes:
        channel (Channel): Канал RabbitMQ для коммуникации
    
    TODO: 
        Количество успешных/неуспешных аутентификаций
        Время ответа auth сервиса
        Количество ретраев
        Типы ошибок
    """
    async def send_auth_message(self, action: AuthAction, data: dict) -> Tuple[dict, Optional[str]]:
        message = {
            "action": action.value, 
            "data": data
        }
        return await self.send_and_wait(
            routing_key="auth_queue", 
            message=message
        )

from .base import MessageProducer

class AuthMessageProducer(MessageProducer):
    async def send_auth_message(self, action: str, data: dict) -> dict:
        message = {"action": action, "data": data}
        return await self.send_and_wait("auth_queue", message)

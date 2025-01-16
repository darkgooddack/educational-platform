from .base import MessageProducer

class HealthMessageProducer(MessageProducer):
    async def check_health(self) -> bool:
        try:
            response = await self.send_and_wait(
                routing_key="health_check", 
                message={"status": "check"})
            return response.get("status") == "healthy"
        except Exception:
            return False

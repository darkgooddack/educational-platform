import json
from aio_pika import Message, Channel

class MessageProducer:

    def __init__(self, channel: Channel) -> None:
        self.channel = channel
    
    async def send_and_wait(self, routing_key: str, message: dict) -> dict:
        queue = await self.channel.declare_queue("", exclusive=True)
        
        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(message).encode(),
                reply_to=queue.name,
                expiration=30000
                ),
                routing_key=routing_key,
        )
        

        async with queue.iterator(timeout=30) as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    return json.loads(message.body.decode())
    
        return {"error": "Timeout"}
    
 
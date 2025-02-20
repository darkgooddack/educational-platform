import json
from aio_pika import Message, connect_robust
from app.core.config import config

class EmailProducer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "email_queue"

    async def connect(self):
        self.connection = await connect_robust(**config.rabbitmq_params)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue(self.queue_name)

    async def send_email_task(self, to_email: str, subject: str, body: str):
        if not self.connection:
            await self.connect()

        message = {
            "to_email": to_email,
            "subject": subject,
            "body": body
        }

        await self.channel.default_exchange.publish(
            Message(json.dumps(message).encode()),
            routing_key=self.queue_name
        )
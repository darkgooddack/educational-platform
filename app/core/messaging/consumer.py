import json
from aio_pika import connect_robust
from app.core.config import config
from app.services.v1.email.service import EmailService

class EmailConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "email_queue"
        self.email_service = EmailService()

    async def connect(self):
        self.connection = await connect_robust(**config.rabbitmq_params)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name)

    async def process_message(self, message):
        async with message.process():
            body = json.loads(message.body.decode())
            await self.email_service.send_email(
                to_email=body["to_email"],
                subject=body["subject"],
                body=body["body"]
            )

    async def run(self):
        if not self.connection:
            await self.connect()

        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self.process_message(message)

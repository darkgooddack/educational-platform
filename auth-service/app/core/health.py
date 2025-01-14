# """
# Модуль проверки здоровья сервиса через RabbitMQ.

# Когда API Gateway проверяет здоровье сервисов:
# 1. API Gateway отправляет сообщение в очередь health_check
# 2. Auth Service получает это сообщение
# 3. Если Auth Service жив - он подтверждает получение сообщения
# 4. API Gateway видит подтверждение и понимает что сервис жив
# """
# import json
# from aio_pika import IncomingMessage, Message, Channel
# from fastapi import FastAPI
# from sqlalchemy import text
# from app.core.dependencies import get_db_session

# async def setup_health_check(_app: FastAPI, channel: Channel) -> None:
#     """
#     Настраивает обработчик health check сообщений.

#     Args:
#         app: FastAPI приложение
#         channel: Канал RabbitMQ для работы с очередями

#     Создает очередь health_check и подписывается на сообщения.
#     При получении сообщения просто подтверждает его получение,
#     сигнализируя что сервис жив.
#     """
    # async def health_callback(message: IncomingMessage) -> None:
    #     try:
    #         # Проверяем БД
    #         async with get_db_session() as session:
    #             await session.execute(text("SELECT 1"))

    #             async with message.process():
    #                 await message.channel.default_exchange.publish(
    #                     Message(
    #                         body=json.dumps({"status": "healthy"}).encode(),
    #                         content_type="application/json"
    #                     ),
    #                     routing_key=message.reply_to
    #                 )
    #     except Exception:
    #         async with message.process():
    #             await message.channel.default_exchange.publish(
    #                 Message(
    #                     body=json.dumps({"status": "unhealthy"}).encode(),
    #                     content_type="application/json"
    #                 ),
    #                 routing_key=message.reply_to
    #             )

#     queue = await channel.declare_queue(
#         "health_check",
#         durable=True,
#         auto_delete=False
#     )
#     await queue.consume(health_callback)

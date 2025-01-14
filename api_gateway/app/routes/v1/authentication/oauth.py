"""
Модуль для OAuth2 аутентификации через социальные сети.

Поддерживаемые провайдеры:
- VK 
- Google
- Yandex

Процесс аутентификации:
1. Редирект на страницу авторизации провайдера
2. Получение кода авторизации
3. Обмен кода на access token
4. Получение данных пользователя
5. Отправка данных в auth-service

TODO:
1. Регистрация приложения у провайдеров:
- VK: https://vk.com/dev
- Google: https://console.cloud.google.com
- Yandex: https://oauth.yandex.ru

2. Добавить записи в id и secret в env

3. Настроить redirect_uri в личных кабинетах провайдеров, указав URL вида:
https://{domain.ru}/api/v1/oauth/{provider}/callback

4. Проверить работопособность

"""
import json
from aio_pika import Connection, Message
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
import aiohttp
from typing import Annotated
from app.core.dependencies import get_redis, get_rabbitmq
from app.core.config import config
from app.schemas import OAuthResponse
from redis import Redis

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/{provider}", response_class=RedirectResponse)
async def oauth_login(provider: str) -> RedirectResponse:
    """
    Редирект на страницу авторизации провайдера.
    
    Args:
        provider (str): Имя провайдера (vk/google/yandex)
        
    Returns:
        RedirectResponse: Редирект на страницу авторизации
        
    Raises:
        HTTPException: Если провайдер не поддерживается
    """
    if provider not in config.oauth_providers:
        raise HTTPException(status_code=400, detail="Неподдерживаемый провайдер")
    
    provider_data = config.oauth_providers[provider]
    params = {
        "client_id": config.oauth_providers[provider]["client_id"],
        "redirect_uri": f"{config.app_url}/api/v1/oauth/{provider}/callback",
        "scope": provider_data["scope"],
        "response_type": "code"
    }
    
    auth_url = f"{provider_data['auth_url']}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
    return RedirectResponse(auth_url)

@router.get("/{provider}/callback", response_model=OAuthResponse)
async def oauth_callback(
    provider: str,
    code: str,
    redis: Annotated[Redis, Depends(get_redis)],
    rabbitmq: Annotated[Connection, Depends(get_rabbitmq)]
) -> OAuthResponse:
    """
    Обработка ответа от OAuth провайдера.
    
    Args:
        provider (str): Имя провайдера
        code (str): Код авторизации от провайдера
        redis: Redis клиент для кэширования токена
        rabbitmq: RabbitMQ соединение для общения с auth-service
        
    Returns:
        OAuthResponse: Токен доступа и провайдер
        
    Raises:
        HTTPException: При ошибке получения токена или данных пользователя
    """
    if provider not in config.oauth_providers:
        raise HTTPException(status_code=400, detail="Неподдерживаемый провайдер")

    # Получение access token
    provider_data = config.oauth_providers[provider]
    token_params = {
        "client_id": config.oauth_providers[provider]["client_id"],
        "client_secret": config.oauth_providers[provider]["client_secret"],
        "code": code,
        "redirect_uri": f"{config.app_url}/api/v1/oauth/{provider}/callback",
        "grant_type": "authorization_code"
    }

    async with aiohttp.ClientSession() as session:
        # Получение токена от провайдера
        async with session.post(provider_data["token_url"], data=token_params) as resp:
            token_data = await resp.json()
            if "error" in token_data:
                raise HTTPException(status_code=400, detail=token_data["error"])
            
        # Получение данных пользователя
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        async with session.get(provider_data["user_info_url"], headers=headers) as resp:
            user_data = await resp.json()

    # Отправка данных в auth-service
    async with rabbitmq.channel() as channel:
        queue = await channel.declare_queue("auth_queue")
        await channel.default_exchange.publish(
            Message(
                body=json.dumps({
                    "action": "oauth_authenticate",
                    "provider": provider,
                    "user_data": user_data
                }).encode()
            ),
            routing_key="auth_queue"
        )
        
        # Получение ответа от auth-service
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    response_data = json.loads(message.body.decode())
                    # Преобразуем ответ в схему
                    oauth_response = OAuthResponse(
                        access_token=response_data["access_token"],
                        token_type="bearer",
                        provider=provider,
                        email=user_data["email"]
                    )

                    if oauth_response.access_token:
                        await redis.setex(
                            f"token:{oauth_response.access_token}",
                            3600,
                            oauth_response.email
                        )

                    return oauth_response

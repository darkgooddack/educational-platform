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

TODO:
- Enum для провайдеров вместо строк
- Вынос конфигурации провайдера в отдельный модуль
- Разделение получения токена и данных пользователя
- Разные коды ошибок для разных проблем
- Асинхронное кэширование токена
- Типизация всех параметров
"""

import logging
from typing import Annotated

import aiohttp
from aio_pika import Connection
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from redis import Redis

from app.core.config import config
from app.core.dependencies import get_rabbitmq, get_redis
from app.core.messaging.auth import AuthAction, AuthMessageProducer
from app.schemas import OAuthResponse

logger = logging.getLogger(__name__)


def setup_routes(router: APIRouter):
    """
    Настройка маршрутов для OAuth2 аутентификации.

    Args:
        router (APIRouter): Роутер FastAPI

    Routes:
        GET /{provider}:
            Редирект на страницу авторизации провайдера.
        GET /{provider}/callback:
            Обработка callback запроса от провайдера.
    """

    @router.get("/{provider}", response_class=RedirectResponse)
    async def oauth_login(provider: str) -> RedirectResponse:
        """
        🌐 Редирект на страницу авторизации провайдера.

        - **provider**: Имя провайдера (vk/google/yandex)

        **Returns**:
        - **RedirectResponse**: Редирект на страницу авторизации

        **Raises**: 
        - **HTTPException**: Если провайдер не поддерживается
        """
        if provider not in config.oauth_providers:
            raise HTTPException(status_code=400, detail="Неподдерживаемый   провайдер")

        provider_config = config.oauth_providers[provider]

        required_fields = ["client_id", "client_secret"]
        # "auth_url", "token_url", "user_info_url", "scope" - по-умолчанию в конфиге
        missing = [field for field in required_fields if field not in provider_config]

        if missing:
            raise HTTPException(
                status_code=500,
                detail=f"Отсутствуют обязательные поля конфигурации: {', '.join (missing)}",
            )

        params = {
            "client_id": provider_config["client_id"],
            "redirect_uri": f"{config.app_url}/api/v1/oauth/{provider}/callback",
            "scope": provider_config["scope"],
            "response_type": "code",
        }

        auth_url = f"{config.oauth_providers[provider]['auth_url']}?{'&'.join(f'{k}=    {v}' for k,v in params.items())}"
        return RedirectResponse(auth_url)

    @router.get("/{provider}/callback", response_model=OAuthResponse)
    async def oauth_callback(
        provider: str,
        code: str,
        redis: Annotated[Redis, Depends(get_redis)],
        rabbitmq: Annotated[Connection, Depends(get_rabbitmq)],
    ) -> OAuthResponse:
        """
        🔄 Обработка ответа от OAuth провайдера.

        - **provider**: Имя провайдера
        - **code**: Код авторизации от провайдера
        - **redis**: Redis клиент для кэширования токена
        - **rabbitmq**: RabbitMQ соединение для общения с auth-service

        **Returns**:
        - **OAuthResponse**: Токен доступа и провайдер

        **Raises**:
        - **HTTPException**: При ошибке получения токена или данных пользователя
        """

        logger.info("OAuth провайдер: %s", provider)

        if provider not in config.oauth_providers:
            raise HTTPException(status_code=400, detail="Неподдерживаемый   провайдер")

        # Получение access token
        provider_data = config.oauth_providers[provider]
        token_params = {
            "client_id": provider_data["client_id"],
            "client_secret": provider_data["client_secret"],
            "code": code,
            "redirect_uri": f"{config.app_url}/api/v1/oauth/{provider}/callback",
            "grant_type": "authorization_code",
        }

        async with aiohttp.ClientSession() as session:
            # Получение токена от провайдера
            async with session.post(
                provider_data["token_url"], data=token_params
            ) as resp:
                token_data = await resp.json()
                if "error" in token_data:
                    raise HTTPException(status_code=400, detail=token_data["error"])

            # Получение данных пользователя
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            async with session.get(
                provider_data["user_info_url"], headers=headers
            ) as resp:
                user_data = await resp.json()

        # Отправка данных в auth-service
        async with rabbitmq.channel() as channel:
            producer = AuthMessageProducer(channel)
            response, error = await producer.send_auth_message(
                AuthAction.OAUTH_AUTHENTICATE,
                data={"provider": provider, "user_data": user_data},
            )

            if error:
                raise HTTPException(
                    status_code=503, detail=f"Auth service error:   {error}"
                )

            # Получение ответа от auth-service
            oauth_response = OAuthResponse(
                access_token=response["access_token"],
                token_type="bearer",
                provider=provider,
                email=user_data["email"],
            )

            # Кэширование токена в Redis
            if oauth_response.access_token:
                redis.setex(
                    f"token:{oauth_response.access_token}", 3600, oauth_response.email
                )

            return oauth_response


__all__ = ["setup_routes"]

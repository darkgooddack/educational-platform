import hashlib
import secrets
from base64 import urlsafe_b64encode
from urllib.parse import urlencode

from fastapi.responses import RedirectResponse

from app.core.exceptions import OAuthTokenError, OAuthUserDataError
from app.schemas import (OAuthProvider, OAuthProviderResponse, VKOAuthParams,
                         VKUserData, VKOAuthTokenParams, VKTokenData)
from app.services.v1.oauth.base import BaseOAuthProvider


class VKOAuthProvider(BaseOAuthProvider):
    """
    OAuth провайдер для VK.
    
    Особенности:
    - Использует PKCE (Proof Key for Code Exchange) для безопасности
    - Email может отсутствовать в ответе от API
    - Требует code_verifier для получения токена
    - Использует state для CSRF защиты
    
    Flow:
    1. Генерация code_verifier и code_challenge для PKCE
    2. Сохранение code_verifier в Redis с привязкой к state
    3. Редирект на VK с code_challenge и state
    4. Получение code и state от VK
    5. Получение code_verifier из Redis по state
    6. Обмен code + code_verifier на токен
    7. Получение данных пользователя
    """

    def __init__(self, session):
        """
        Инициализация VK OAuth провайдера.
    
        Args:
            session: Сессия базы данных
        """
        super().__init__(provider=OAuthProvider.VK.value, session=session)

    async def get_auth_url(self) -> RedirectResponse:
        """
        Формирование URL для OAuth авторизации через VK с PKCE.
        
        Генерирует code_verifier, создает code_challenge и сохраняет verifier в Redis.
        
        Returns:
            RedirectResponse: URL для перенаправления на страницу входа VK
        """
        code_verifier = secrets.token_urlsafe(64)

        params = VKOAuthParams(
            client_id=self.config.client_id,
            redirect_uri=await self._get_callback_url(),
            code_challenge=self._generate_code_challenge(code_verifier),
            scope=self.config.scope,
        )
 
        redis_key = f"vk_verifier_{params.state}"
        await self._redis_storage.set(
            key=redis_key,
            value=code_verifier,
            expires=300
        )

        auth_url = f"{self.config.auth_url}?{urlencode(params.model_dump())}"
        return RedirectResponse(url=auth_url)

    async def get_token(self, code: str, state: str = None, device_id: str = None) -> VKTokenData:
        """
        Получение токена от VK по коду авторизации.
        
        Args:
            code: Код авторизации от VK
            state: Параметр state для проверки CSRF
            device_id: ID устройства для VK API
            
        Returns:
            VKTokenData: Токен доступа и связанные данные
            
        Raises:
            OAuthTokenError: При отсутствии кода или ошибке от VK API
        """
        if not code:
            raise OAuthTokenError(self.provider, "Не передан код авторизации")

        token_params = VKOAuthTokenParams(
            redirect_uri=str(await self._get_callback_url()),
            code=code,
            client_id=str(self.config.client_id), # да, пиздец, но так надо
            device_id=device_id,
            state=state,
        )

        if state:
            redis_key = f"vk_verifier_{state}"
            verifier = await self._redis_storage.get(redis_key)

            if isinstance(verifier, bytes):
                verifier = verifier.decode('utf-8')

            if verifier:
                token_params.code_verifier = verifier
                await self._redis_storage.delete(redis_key)

        token_data = await self.http_client.get_token(
            self.config.token_url,
            token_params.to_dict()
        )

        if "error" in token_data:
            raise OAuthTokenError(
                self.provider,
                f"Ошибка получения токена: {token_data.get('error_description', token_data['error'])}"
            )

        return VKTokenData(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "bearer"),
            expires_in=token_data["expires_in"],
            user_id=token_data["user_id"],
            email=token_data.get("email"),
            state=state,
            scope=token_data.get("scope")
        )

    async def get_user_info(self, token: str) -> VKUserData:
        """
        Получение данных пользователя через VK API.
        
        Использует стандартный эндпоинт VK для получения 
        информации о пользователе. Возвращает данные в формате VKUserData.
        
        Args:
            token: Токен доступа от VK
            
        Returns:
            VKUserData: Данные пользователя в унифицированном формате
        """
        return await super().get_user_info(token, client_id=self.config.client_id)
    
    def _get_email(self, user_data: VKUserData) -> str:
        """
        Получение email пользователя.
        VK может не предоставить email если пользователь не разрешил доступ.
        
        Raises:
            OAuthUserDataError: Если email отсутствует
        """
        if not user_data.email:
            raise OAuthUserDataError(self.provider, "VK не предоставил email")
        return user_data.email

    def _generate_code_challenge(self, verifier: str) -> str:
        """
        Генерация code_challenge для PKCE.
        
        Args:
            verifier: Сгенерированный code_verifier
            
        Returns:
            str: code_challenge в формате base64url(sha256(verifier))
        """
        return (
            urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )

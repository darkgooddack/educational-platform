import hashlib
import secrets
from base64 import urlsafe_b64encode
from urllib.parse import urlencode

from fastapi.responses import RedirectResponse

from app.core.exceptions import OAuthTokenError, OAuthUserDataError
from app.schemas import (OAuthProvider, OAuthProviderResponse, VKOAuthParams,
                         VKUserData)
from app.services.v1.oauth.base import BaseOAuthProvider


class VKOAuthProvider(BaseOAuthProvider):
    """
    OAuth провайдер для VK

    Особенности:
    - Использует PKCE (Proof Key for Code Exchange)
    - Email может отсутствовать в ответе
    - Требуется code_verifier для получения токена
    """

    def __init__(self, session):
        super().__init__(provider=OAuthProvider.VK.value, session=session)

    async def get_token(self, code: str, state: str = None) -> OAuthProviderResponse:
        """
        Получение токена
        """
        self.logger.debug(f"Получаем токен с кодом: {code}, state: {state}")
    
        token_params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "redirect_uri": str(await self._get_callback_url())
        }
    
        if state:
            await self._handle_state(state, token_params)
    
        return await self.http_client.get_token(
            self.config.token_url, 
            token_params
        )
        # return await super().get_token(code, state)

    async def _get_callback_url(self) -> str:
        """Стандартный callback URL"""
        return await super()._get_callback_url()

    async def get_user_info(self, token: str) -> VKUserData:
        """Стандартное получение данных пользователя"""
        return await super().get_user_info(token)

    def _get_email(self, user_data: VKUserData) -> str:
        """
        VK может не предоставить email если пользователь не разрешил доступ
        """
        if not user_data.email:
            raise OAuthUserDataError(self.provider, "VK не предоставил email")
        return user_data.email

    def _generate_code_challenge(self, verifier: str) -> str:
        """Генерация code_challenge для PKCE"""
        return (
            urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
            .decode()
            .rstrip("=")
        )

    async def get_auth_url(self) -> RedirectResponse:
        """URL авторизации с PKCE"""
        code_verifier = secrets.token_urlsafe(64)
        state = secrets.token_urlsafe()

        redis_key = f"vk_verifier_{state}"
        await self._redis_storage.set(
            key=redis_key, 
            value=code_verifier, 
            expires=300
        )

        params = VKOAuthParams(
            client_id=self.config.client_id,
            redirect_uri=await self._get_callback_url(),
            scope=self.config.scope,
            state=state, # Используем то же значение state
            code_challenge=self._generate_code_challenge(code_verifier),
            code_challenge_method="S256",
        )       
        
        auth_url = f"{self.config.auth_url}?{urlencode(params.model_dump())}"
        return RedirectResponse(url=auth_url)

    async def _handle_state(self, state: str, token_params: dict) -> None:
        """Добавление code_verifier в параметры токена"""
        if not state:
            raise OAuthTokenError(self.provider, "Отсутствует параметр state")
        
        redis_key = f"vk_verifier_{state}"
        verifier = await self._redis_storage.get(redis_key)
        
        if not verifier:
            raise OAuthTokenError(self.provider, "Неверный state или истек срок verifier") 

        token_params["code_verifier"] = verifier
        await self._redis_storage.delete(redis_key)

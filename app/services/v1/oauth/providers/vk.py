from base64 import urlsafe_b64encode
import hashlib
import secrets
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse
from app.services.v1.oauth.base import BaseOAuthProvider
from app.schemas import OAuthProvider, VKUserData, VKOAuthParams, OAuthProviderResponse
from app.core.exceptions import OAuthTokenError, OAuthUserDataError

class VKOAuthProvider(BaseOAuthProvider):
    """
    OAuth провайдер для VK

    Особенности:
    - Использует PKCE (Proof Key for Code Exchange)
    - Email может отсутствовать в ответе
    - Требуется code_verifier для получения токена
    """

    def __init__(self, session):
        super().__init__(
            provider=OAuthProvider.VK.value,
            session=session
        )

    async def get_token(self, code: str, state: str = None) -> OAuthProviderResponse:
        """Стандартное получение токена"""
        return await super().get_token(code)

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
        return urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()
        ).decode().rstrip('=')

    async def get_auth_url(self) -> RedirectResponse:
        """URL авторизации с PKCE"""
        code_verifier = secrets.token_urlsafe(64)
        state = secrets.token_urlsafe()

        await self._redis_storage.set(
            f"vk_verifier_{state}",
            code_verifier
        )

        params = VKOAuthParams(
            client_id=self.config.client_id,
            redirect_uri=await self._get_callback_url(),
            scope=self.config.scope,
            state=state,
            code_challenge=self._generate_code_challenge(code_verifier),
            code_challenge_method='S256'
        )

        auth_url = f"{self.config.auth_url}?{urlencode(params.model_dump())}"
        return RedirectResponse(url=auth_url)

    async def _handle_state(self, state: str, token_params: dict) -> None:
        """Добавление code_verifier в параметры токена"""
        verifier = await self._redis_storage.get(f"vk_verifier_{state}")
        if not verifier:
            raise OAuthTokenError(self.provider, "Invalid state/verifier")

        token_params["code_verifier"] = verifier
        await self._redis_storage.delete(f"vk_verifier_{state}")

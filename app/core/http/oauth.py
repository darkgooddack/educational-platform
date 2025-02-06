from .base import BaseHttpClient
from aiohttp.client_exceptions import ContentTypeError

class OAuthHttpClient(BaseHttpClient):
    async def get_token(self, url: str, params: dict) -> dict:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = await self.post(url, data=params, headers=headers)
            return response
        except ContentTypeError as e:
            # Проверяем наличие response и возможности получить текст
            if hasattr(e, 'response') and e.response:
                html_content = await e.response.text()
                self.logger.error("HTML Response: %s", html_content)
            self.logger.error("ContentTypeError details: %s", e.__dict__)
            raise
        except Exception as e:
            self.logger.error("Unexpected error: %s", str(e))
            raise

    async def get_user_info(self, url: str, token: str) -> dict:
        headers = {"Authorization": f"Bearer {token}"}
        return await self.get(url, headers=headers)

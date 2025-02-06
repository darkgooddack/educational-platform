from .base import BaseHttpClient


class OAuthHttpClient(BaseHttpClient):
    async def get_token(self, url: str, params: dict) -> dict:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = await self.post(url, data=params, headers=headers)
        
        if response.get('content_type') == 'text/html':
            html_content = await response.text()
            self.logger.error("HTML Response: %s", html_content)
            
        return response

    async def get_user_info(self, url: str, token: str) -> dict:
        headers = {"Authorization": f"Bearer {token}"}
        return await self.get(url, headers=headers)

from .base import BaseHttpClient


class OAuthHttpClient(BaseHttpClient):
    async def get_token(self, url: str, params: dict) -> dict:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return await self.post(url, data=params, headers=headers)

    async def get_user_info(self, url: str, token: str) -> dict:
        headers = {"Authorization": f"Bearer {token}"}
        return await self.get(url, headers=headers)

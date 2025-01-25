import aiohttp
from typing import Optional

class BaseHttpClient:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get(self, url: str, headers: dict = None) -> dict:
        session = await self._get_session()
        async with session.get(url, headers=headers) as resp:
            return await resp.json()

    async def post(self, url: str, data: dict = None, headers: dict = None) -> dict:
        session = await self._get_session()
        async with session.post(url, data=data, headers=headers) as resp:
            return await resp.json()
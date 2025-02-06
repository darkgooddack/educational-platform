import logging
from typing import Optional

import aiohttp


class BaseHttpClient:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get(self, url: str, headers: dict = None) -> dict:
        session = await self._get_session()
        self.logger.debug("GET запрос к %s", url)
        async with session.get(url, headers=headers) as resp:
            return await resp.json()

    async def post(self, url: str, data: dict = None, headers: dict = None) -> dict:
        if data:
            # Фильтруем None значения из параметров
            data = {k: v for k, v in data.items() if v is not None}

        session = await self._get_session()
        self.logger.debug("POST запрос к %s с данными %s", url, data)
        async with session.post(url, data=data, headers=headers) as resp:
            return await resp.json()

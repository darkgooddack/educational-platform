from .base import BaseHttpClient
from aiohttp.client_exceptions import ContentTypeError

class OAuthHttpClient(BaseHttpClient):
    async def get_token(self, url: str, params: dict) -> dict:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.logger.debug("Получение токена от %s с параметрами %s", url, params)
        try:
            response = await self.post(url, data=params, headers=headers)
            self.logger.info("Токен успешно получен от %s", url)
            return response

        except ContentTypeError as e:
            if hasattr(e, 'response') and e.response:
                html_content = await e.response.text()
                self.logger.error("Ошибка получения токена. HTML ответ: %s", html_content)
            self.logger.error("ContentTypeError: %s", e.__dict__)
            raise
        except Exception as e:
            self.logger.error("Неожиданная ошибка при получении токена: %s", str(e))
            raise

    async def get_user_info(self, url: str, token: str) -> dict:
        headers = {"Authorization": f"Bearer {token}"}
        self.logger.debug("Получение информации о пользователе от %s", url)

        response = await self.get(url, headers=headers)
        self.logger.info("Информация о пользователе успешно получена от %s", url)
        return response

from typing import Optional

from aiohttp.client_exceptions import ContentTypeError

from .base import BaseHttpClient


class OAuthHttpClient(BaseHttpClient):
    def _format_log_message(self, data: dict) -> str:
        return "\n".join(f"    {k}: {v}" for k, v in data.items())

    async def get_token(self, url: str, params: dict) -> dict:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        self.logger.debug(
            "Получение токена от %s с параметрами:\n%s",
            url,
            self._format_log_message(params),
        )

        try:
            response = await self.post(url, data=params, headers=headers)
            self.logger.info("Токен успешно получен от %s", url)
            self.logger.debug(
                "Ответ от сервера:\n%s", self._format_log_message(response)
            )
            return response

        except ContentTypeError as e:
            if hasattr(e, "response") and e.response:
                html_content = await e.response.text()
                self.logger.error(
                    "Ошибка получения токена. HTML ответ:\n%s",
                    self._format_log_message({"html": html_content}),
                )
            self.logger.error(
                "ContentTypeError:\n%s", self._format_log_message(e.__dict__)
            )
            raise
        except Exception as e:
            self.logger.error("Неожиданная ошибка при получении токена: %s", str(e))
            raise

    async def get_user_info(
        self, url: str, token: str, client_id: Optional[str] = None
    ) -> dict:
        headers = {"Authorization": f"Bearer {token}"}
        params = {}

        if client_id:
            params["client_id"] = client_id

        self.logger.debug(
            "Получение информации о пользователе от %s\nЗаголовки:\n%s\nПараметры:\n%s",
            url,
            self._format_log_message(headers),
            self._format_log_message(params),
        )

        response = await self.get(url, headers=headers, params=params)

        self.logger.info("Информация о пользователе успешно получена от %s", url)
        self.logger.debug("Ответ от сервера:\n%s", self._format_log_message(response))
        return response

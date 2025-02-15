import logging
from typing import Callable, Dict, TypeVar

from app.core.exceptions import OAuthUserDataError
from app.schemas import GoogleUserData, VKUserData, YandexUserData

T = TypeVar("T", YandexUserData, GoogleUserData, VKUserData)


class BaseOAuthHandler:
    """Базовый обработчик данных от OAuth провайдеров"""

    def __init__(self, provider: str):
        self.provider = provider
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{provider}")

    def validate_required_fields(self, data: dict, fields: list) -> None:
        """Проверка обязательных полей"""
        missing = [f for f in fields if not data.get(f)]
        if missing:
            raise OAuthUserDataError(
                self.provider, f"Отсутствуют обязательные поля: {', '.join(missing)}"
            )

    def clean_name(self, name: str | None) -> str | None:
        """Очистка и валидация имени"""
        if not name:
            return None
        return name.strip()[:50]  # Ограничение из RegistrationSchema


class YandexHandler(BaseOAuthHandler):
    async def __call__(self, data: dict) -> YandexUserData:
        """
        Обработка данных пользователя от Яндекса.

        Преобразует "сырые" данные от Яндекс API в унифицированный формат.
        Проверяет наличие обязательного поля default_email.

        Args:
            user_data: Словарь с данными от Яндекс API
                - id: Идентификатор пользователя
                - default_email: Основной email (обязательное поле)
                - first_name: Имя пользователя
                - last_name: Фамилия
                - avatar: URL аватара
                - login: Логин
                - emails: Список всех email адресов
                - psuid: ID в системе Яндекс

        Returns:
            YandexUserData: Структурированные данные пользователя

        Raises:
            OAuthUserDataError: Если отсутствует default_email
        """
        self.validate_required_fields(data, ["id", "default_email"])

        return YandexUserData(
            id=str(data["id"]),
            email=data["default_email"],
            first_name=self.clean_name(data.get("first_name")),
            last_name=self.clean_name(data.get("last_name")),
            avatar=data.get("avatar"),
            default_email=data["default_email"],
            login=data.get("login"),
            emails=data.get("emails", []),
            psuid=data.get("psuid"),
        )


class GoogleHandler(BaseOAuthHandler):
    async def __call__(self, data: dict) -> GoogleUserData:
        """
        Обработка данных пользователя от Google.

        Преобразует данные от Google API в унифицированный формат.
        Обрабатывает специфичные для Google поля given_name и family_name.

        Args:
            user_data: Словарь с данными от Google API
                - id: Идентификатор пользователя
                - email: Email пользователя
                - verified_email: Флаг верификации email
                - given_name: Имя
                - family_name: Фамилия
                - picture: URL фото профиля

        Returns:
            GoogleUserData: Структурированные данные пользователя
        """
        self.validate_required_fields(data, ["id", "email"])

        return GoogleUserData(
            id=str(data["id"]),
            email=data.get("email"),
            first_name=self.clean_name(data.get("given_name")),
            last_name=self.clean_name(data.get("family_name")),
            avatar=data.get("picture"),
            verified_email=bool(data.get("verified_email")),
            given_name=data.get("given_name"),
            family_name=data.get("family_name"),
            picture=data.get("picture"),
        )


class VKHandler(BaseOAuthHandler):
    async def __call__(self, data: dict) -> VKUserData:
        """
        Обработка данных пользователя от VK.

        Преобразует данные от VK API в унифицированный формат.
        Проверяет наличие обязательных полей user и user_id.
        Логирует предупреждение если отсутствует email.

        Args:
            user_data: Словарь с данными от VK API
                - user: Объект с данными пользователя
                    - user_id: ID пользователя (обязательное)
                    - email: Email пользователя
                    - first_name: Имя
                    - last_name: Фамилия
                    - avatar: URL фото
                    - phone: Номер телефона

        Returns:
            VKUserData: Структурированные данные пользователя

        Raises:
            OAuthUserDataError: Если отсутствуют данные пользователя или user_id
        """
        user = data.get("user", {})
        self.validate_required_fields(user, ["user_id", "email"])

        return VKUserData(
            id=str(user["user_id"]),
            email=user.get("email"),
            first_name=self.clean_name(user.get("first_name")),
            last_name=self.clean_name(user.get("last_name")),
            avatar=user.get("avatar"),
            phone=user.get("phone"),
            user_id=str(user["user_id"]),
        )


# Маппинг провайдеров к функциям
PROVIDER_HANDLERS: Dict[str, BaseOAuthHandler] = {
    "yandex": YandexHandler("yandex"),
    "google": GoogleHandler("google"),
    "vk": VKHandler("vk"),
}

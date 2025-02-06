from typing import Callable, Dict, TypeVar
from app.core.exceptions import OAuthUserDataError
from app.schemas import GoogleUserData, VKUserData, YandexUserData

T = TypeVar('T', YandexUserData, GoogleUserData, VKUserData)

async def get_yandex_user_info(user_data: dict) -> YandexUserData:
    """
    Обработка данных пользователя от Яндекса

    Attributes:
        user_data (dict): Данные пользователя

    Returns:
        dict: Обработанные данные пользователя
    """
    if not user_data.get("default_email"):
        raise OAuthUserDataError(
            "yandex",
            "Email не предоставлен. Убедитесь что у аккаунта Яндекс есть email",
        )

    return YandexUserData(
        id=str(user_data["id"]),
        email=email,
        first_name=user_data.get("first_name") or None,
        last_name=user_data.get("last_name") or None,
        avatar=user_data.get("avatar") or None,
        default_email=email,
        login=user_data.get("login") or None,
        emails=emails_list,
        psuid=user_data.get("psuid") or None,
    )


async def get_google_user_info(user_data: dict) -> GoogleUserData:
    """
    Обработка данных пользователя от Google

    Attributes:
        user_data (dict): Данные пользователя

    Returns:
        dict: Обработанные данные пользователя
    """
    given_name = user_data.get("given_name") or None
    family_name = user_data.get("family_name") or None
    picture = user_data.get("picture") or None

    return GoogleUserData(
        id=str(user_data["id"]),
        email=user_data.get("email") or None,
        first_name=given_name,
        last_name=family_name,
        avatar=picture,
        verified_email=bool(user_data.get("verified_email", False)),
        given_name=given_name,
        family_name=family_name,
        picture=picture
    )


async def get_vk_user_info(user_data: dict) -> VKUserData:
    """
    Обработка данных пользователя от VK

    Attributes:
        user_data (dict): Данные пользователя

    Returns:
        dict: Обработанные данные пользователя
    """
    user = user_data.get("user", {})
    user_id = user.get("user_id", "")

    return VKUserData(
        id=str(user_id),
        email=user.get("email") or None,
        first_name=user.get("first_name") or None,
        last_name=user.get("last_name") or None,
        avatar=user.get("avatar") or None,
        phone=user.get("phone") or None,
        user_id=str(user_id)
    )


# Маппинг провайдеров к функциям
PROVIDER_HANDLERS: Dict[str, Callable[[dict], T]] = {
    "yandex": get_yandex_user_info,
    "google": get_google_user_info,
    "vk": get_vk_user_info,
}

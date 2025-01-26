from app.core.exceptions import OAuthUserDataError
from app.schemas import GoogleUserData, VKUserData, YandexUserData


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
        id=user_data["id"],
        email=user_data["default_email"],
        first_name=user_data.get("first_name", ""),
        last_name=user_data.get("last_name", ""),
        default_email=user_data["default_email"],
        login=user_data.get("login"),
        emails=user_data.get("emails", []),
        psuid=user_data.get("psuid"),
    )


async def get_google_user_info(user_data: dict) -> GoogleUserData:
    """
    Обработка данных пользователя от Google

    Attributes:
        user_data (dict): Данные пользователя

    Returns:
        dict: Обработанные данные пользователя
    """
    return GoogleUserData(
        id=user_data["id"],
        email=user_data["email"],
        first_name=user_data.get("given_name", ""),
        last_name=user_data.get("family_name", ""),
        avatar=user_data.get("picture"),
        verified_email=user_data.get("verified_email", False),
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
    return VKUserData(
        id=user.get("user_id", ""),
        email=user.get("email", ""),
        first_name=user.get("first_name", ""),
        last_name=user.get("last_name", ""),
        phone=user.get("phone", ""),
        avatar=user.get("avatar"),
    )


# Маппинг провайдеров к функциям
PROVIDER_HANDLERS = {
    "yandex": get_yandex_user_info,
    "google": get_google_user_info,
    "vk": get_vk_user_info,
}

from pydantic import EmailStr, Field
from .base import BaseInputSchema

class RegistrationSchema(BaseInputSchema):
    """
    Схема регистрации нового пользователя.

    Attributes:
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        middle_name (str): Отчество пользователя.
        email (str): Email пользователя.
        phone (str): Телефон пользователя.
        password (str): Пароль пользователя.
    """
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50) 
    middle_name: str | None = Field(None, max_length=50)
    email: EmailStr
    phone: str = Field(
        pattern=r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$",
        examples=["+7 (999) 123-45-67"]
    )
    password: str = Field(min_length=8)

class RegistrationResponseSchema(BaseInputSchema):
    """
    Схема ответа при успешной регистрации

    Attributes:
        user_id (int): ID пользователя
        email (str): Email пользователя
        message (str): Сообщение об успешной регистрации
    """
    user_id: int
    email: EmailStr
    message: str = "Регистрация успешно завершена"
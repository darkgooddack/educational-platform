"""
Модуль безопасности приложения.

Содержит функции для работы с секретными ключами и токенами.

Example:
    >>> from app.core.security import TokenMixin
    >>> secret = TokenMixin.get_token_key()

    >>> from app.core.security import HashingMixin
    >>> class UserService(HashingMixin):
    >>>     def create_user(self, password: str):
    >>>         hashed = self.hash_password(password)

"""

import logging
from datetime import datetime, timezone

import passlib
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from app.core.config import config
from app.core.exceptions import (
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    TokenMissingError,
)
from app.schemas import UserCredentialsSchema

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=102400,
    argon2__parallelism=8,
)

logger = logging.getLogger(__name__)


class HashingMixin:
    """
    Миксин для хеширования паролей.

    Предоставляет метод для хеширования паролей с использованием bcrypt.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Генерирует хеш пароля с использованием bcrypt.

        Args:
            password: Пароль для хеширования

        Returns:
            Хешированный пароль
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify(hashed_password: str, plain_password: str) -> bool:
        """
        Проверяет, соответствует ли переданный пароль хешу.
        Args:
            hashed_password: Хеш пароля.
            plain_password: Пароль для проверки.

        Returns:
            True, если пароль соответствует хешу, иначе False.

        """
        try:

            return pwd_context.verify(plain_password, hashed_password)

        except passlib.exc.UnknownHashError:
            logger.warning("Неизвестный формат хеша пароля")
            return False


class TokenMixin:
    """
    Миксин для работы с токенами.

    Предоставляет методы для генерации и проверки токенов.
    """

    @staticmethod
    def generate_token(payload: dict) -> str:
        """
        Генерирует JWT токен.

        Args:
            payload: Данные для токена

        Returns:
            JWT токен
        """
        return jwt.encode(
            payload, key=TokenMixin.get_token_key(), algorithm=config.token_algorithm
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Декодирует JWT токен.

        Args:
            token: JWT токен

        Returns:
            Декодированные данные

        Raises:
            AuthError: При невалидном токене
        """
        try:
            return jwt.decode(
                token,
                key=TokenMixin.get_token_key(),
                algorithms=[config.token_algorithm],
            )
        except ExpiredSignatureError as error:
            raise TokenExpiredError() from error
        except JWTError as error:
            raise TokenInvalidError() from error

    @staticmethod
    def create_payload(user: UserCredentialsSchema) -> dict:
        """
        Создает payload для токена.

        Args:
            user: Данные пользователя

        Returns:
            Payload для JWT
        """
        expires_at = (
            int(datetime.now(timezone.utc).timestamp())
            + TokenMixin.get_token_expiration()
        )
        return {"sub": user.email, "expires_at": expires_at}

    @staticmethod
    def get_token_key() -> str:
        """
        Получает секретный ключ для токена.

        Returns:
            str: Секретный ключ для токена.
        """
        return config.token_key.get_secret_value()

    @staticmethod
    def get_token_expiration() -> int:
        """
        Получает время истечения срока действия токена в секундах.

        Example:
            1440 минут * 60 = 86400 секунд (24 часа)

        Returns:
            int: Количество секунд до истечения токена
        """

        return config.token_expire_minutes * 60

    @staticmethod
    def is_expired(expires_at: str) -> bool:
        """
        Проверяет, истек ли срок действия токена.

        Args:
            expires_at: Время истечения в секундах

        Returns:
            True, если токен истек, иначе False.
        """
        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        return current_timestamp > expires_at

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Проверяет JWT токен и возвращает payload

        Args:
            token: Токен пользователя.

        Returns:
            payload: Данные пользователя.
        """
        if not token:
            raise TokenMissingError()
        return TokenMixin.decode_token(token)

    @staticmethod
    def validate_payload(payload: dict) -> str:
        """
        Валидирует данные из payload

        Args:
            payload: Данные пользователя.

        Returns:
            email: Email пользователя.
        """
        expires_at = (
            int(datetime.now(timezone.utc).timestamp())
            + TokenMixin.get_token_expiration()
        )

        email = payload.get("sub")
        expires_at = payload.get("expires_at")

        if not email:
            raise InvalidCredentialsError()

        if TokenMixin.is_expired(expires_at):
            raise TokenExpiredError()

        return email

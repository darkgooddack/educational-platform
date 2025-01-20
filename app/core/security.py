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

from datetime import datetime, timedelta, timezone
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from app.core.config import config
from app.core.exceptions import TokenExpiredError, TokenInvalidError
from app.schemas import UserSchema, TokenSchema
from app.service import AuthDataManager

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,
    argon2__memory_cost=102400,
    argon2__parallelism=8,
)


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
            payload, 
            key=TokenMixin.get_token_key(), 
            algorithm=config.token_algorithm
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
        except ExpiredSignatureError:
            raise TokenExpiredError()
        except JWTError:
            raise TokenInvalidError()
    
    @staticmethod
    async def create_token(self, user: UserSchema, data_manager: AuthDataManager) -> TokenSchema:
        """
        Создание JWT токена

        Args:
            user: Данные пользователя
            data_manager: Менеджер данных для сохранения токена

        Returns:
            Токен доступа
        """
        # Отличная мысль, но пока нет
        # if not isinstance(user, UserSchema): 
        #     raise ValueError("Expected user to be of type UserSchema")

        payload = TokenMixin.create_payload(user)
        token = TokenMixin.generate_token(payload)
        await data_manager.save_token(user, token)

        return TokenSchema(
            access_token=token, 
            token_type=config.token_type
        )

    @staticmethod
    def create_payload(user: UserSchema) -> dict:
        """
        Создает payload для токена.

        Args:
            user: Данные пользователя

        Returns:
            Payload для JWT
        """
        return {
            "sub": user.email, 
            "expires_at": TokenMixin.get_token_expiration()
        }

    @staticmethod
    def get_token_key() -> str:
        """
        Получает секретный ключ для токена.

        Returns:
            str: Секретный ключ для токена.
        """
        return config.token_key.get_secret_value()

    @staticmethod
    def get_token_expiration() -> str:
        """
        Получает время истечения срока действия токена.
        """
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=config.token_expire_minutes
        )
        return expires_at.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def is_expired(expires_at: str) -> bool:
        """
        Проверяет, истек ли срок действия токена.

        Args:
            expires_at: Время истечения срока действия токена.

        Returns:
            True, если токен истек, иначе False.
        """
        expires_dt = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        return expires_dt < datetime.now(timezone.utc)

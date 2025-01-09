from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal

class Settings(BaseSettings):
    
    TEST_DB_NAME: str
    TEST_DB_PORT: int
    TEST_DB_HOST: str
    TEST_DB_USER: str
    TEST_DB_PASS: str

    POSTGRES_USER: str
    POSTGRES_PASS: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    REGISTRATION_SERVICE_URL: str
    
    # JWT Secret Key
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180  # 3 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 4320  # 3 days

    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: str = "INFO"
    
    # App Secret Key
    SECRET_KEY: str

    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def settings() -> Settings:
    return Settings()

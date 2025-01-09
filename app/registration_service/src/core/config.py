from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    TEST_DB_NAME: str
    TEST_DB_PORT: int
    TEST_DB_HOST: str
    TEST_DB_USER: str
    TEST_DB_PASS: str

    AUTH_SERVICE_URL: str

    POSTGRES_USER: str
    POSTGRES_PASS: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def settings() -> Settings:
    return Settings()
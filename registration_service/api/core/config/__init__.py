from .app_config import AppConfig
from .env_config import Settings

app_config = AppConfig()
env_config = Settings()


__all__ = ["app_config", "env_config"]

from functools import lru_cache

try:  # pragma: no cover - import path
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
except ImportError:  # pragma: no cover - executed only if dependency missing
    from pydantic import BaseModel as _BaseModel  # type: ignore

    class BaseSettings(_BaseModel):  # type: ignore
        """Fallback minimal BaseSettings replacement.
        Install pydantic-settings for full .env support:
            pip install pydantic-settings
        """

    class SettingsConfigDict(dict):  # type: ignore
        def __init__(self, *args, **kwargs):  # mimic constructor but ignore
            super().__init__()

class Settings(BaseSettings):
    app_name: str = "Hord Manager"
    debug: bool = True
    database_url: str = "sqlite:///./hord_manager.db"
    secret_key: str = "CHANGE_ME"

    # Pylance may not resolve SettingsConfigDict type when fallback is active; ignore type.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")  # type: ignore[arg-type]

@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    UPSTAGE_API_KEY: str = ""
    UPSTAGE_MODEL: str = "solar-pro3"
    UPSTAGE_API_URL: str = "https://api.upstage.ai/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

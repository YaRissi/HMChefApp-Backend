"""Settings for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Class for BaseSettings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    REDIS_URL: str 

    SECRET_KEY: str


settings = Settings()
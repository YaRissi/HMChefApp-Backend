"""Settings for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Class for BaseSettings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database settings
    REDIS_URL: str

    # FastAPI settings
    SECRET_KEY: str

    # UploadThing API settings
    UPLOADTHING_SECRET_KEY: str


settings = Settings()

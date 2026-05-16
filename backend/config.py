from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from .env file."""

    ANTHROPIC_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"
    OPUS_MODEL: str = "claude-opus-4-6"
    SONNET_MODEL: str = "claude-sonnet-4-6"

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8"}


settings = Settings()

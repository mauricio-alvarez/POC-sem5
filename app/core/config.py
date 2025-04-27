from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings (BaseSettings):
    APP_NAME: str = "no-name"
    DATABASE_URL: str = "no-database-url"
    SECRET_KEY: str = "no-secret-key"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
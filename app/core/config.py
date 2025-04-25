from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings (BaseSettings):
    APP_NAME: str = "no-name"
    DATABASE_URL: str = "no-database-url"
    SECRET_KEY: str = "no-secret-key"
    
    JWT_SECRET_KEY: str = "no-jwt-secret-key"
    JWT_ALGORITHM: str = "no-jwt-algorithm"
    JWT_EXPIRATION_DELTA_SECONDS: int = 86400
    

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# @lru_cache()
# def get_settings() -> Settings:
#     return Settings()

settings = Settings()
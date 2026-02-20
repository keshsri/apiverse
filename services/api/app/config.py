from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "APIVerse"
    DEBUG: bool = False
    VERSION: str = "0.1.0"

    DATABASE_URL: str

    REDIS_HOST: str
    REDIS_PORT: int = 6379

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRY_IN_MINUTES: int = 60 * 24

    RDS_SECRET_ARN: str = ""
    AWS_REGION: str = 'eu-west-1'

    class Config:
        env_file = ".env"
        case_sensitive = "True"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
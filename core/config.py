from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Transportation Management System"
    DATABASE_URL: str
    DATABASE_NAME: str = "transport_management"

    class Config:
        env_file = ".env"

settings = Settings()
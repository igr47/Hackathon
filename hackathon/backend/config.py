from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "carwash_user"
    DB_PASSWORD: str = "carwash_pass"
    DB_NAME: str = "carwash_db"
    APP_NAME: str = "Car Wash & Auto Detailing API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()

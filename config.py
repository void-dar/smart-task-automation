from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str #= os.getenv("DATABASE_URL")
    JWT_SECRET: str
    JWT_ALGORITM: str
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    SECRET_KEY: str

    
    model_config = SettingsConfigDict(env_file = ".env")

settings = Settings()

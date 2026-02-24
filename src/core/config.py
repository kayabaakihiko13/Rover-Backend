from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig
import os

ENV = os.getenv("ENV","local")
env_file = ".env.local" if ENV == "local" else ".env"

load_dotenv(env_file)

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY_JWT: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    CORS_FE_DEV: str

    MODEL_PATH: str
    LABEL_PATH: str

    # EMAIL CONFIG
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    model_config = SettingsConfigDict(
        env_file=env_file,
        extra="ignore"
    )

settings = Settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True
)
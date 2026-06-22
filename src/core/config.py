from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_mail import ConnectionConfig
import os

# configuration .env file and main.py in root folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV = os.getenv("ENV", "local")
env_file_path = PROJECT_ROOT / (".env.dev" if ENV == "local" else ".env")

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    SECRET_KEY_JWT: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    FORGOT_PASSWORD_TOKEN_EXPIRE_MINUTE:int
    CORS_FE_ORIGINS: str

    MODEL_PATH: str
    LABEL_PATH: str

    # ADMIN CONFIG
    SUPERADMIN_EMAIL: str
    SUPERADMIN_USERNAME: str
    SUPERADMIN_PASSWORD: str

    # EMAIL CONFIG
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    # file object env
    UPLOAD_DIR: str = Field(
        default="/app/uploads", 
        validation_alias="UPLOAD_DIR"
    )

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

def get_email_conf() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
    )
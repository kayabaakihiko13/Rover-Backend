from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

env_file = ".env.local" if os.getenv("ENV", "local") == "local" else ".env"
load_dotenv(env_file)
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY_JWT: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    MODEL_PATH:str
    LABEL_PATH:str
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

settings = Settings()

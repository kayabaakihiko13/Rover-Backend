from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
# initical value in env
ENV = os.getenv("ENV","local")
env_file = ".env.local" if os.getenv("ENV", "local") == "local" else ".env"

# load env 
load_dotenv(env_file)
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY_JWT: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    CORS_FE_DEV: str

    MODEL_PATH: str
    LABEL_PATH: str

    model_config = SettingsConfigDict(
        env_file=env_file,
        extra="ignore"
    )

settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY_JWT: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    MODEL_PATH:str
    LABEL_PATH:str

    model_config = SettingsConfigDict(env_file=".env.local")

settings = Settings()

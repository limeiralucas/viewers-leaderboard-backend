from os import getenv
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_filename():
    env = getenv("ENV")
    return f".env.${env.lower()}" if env else ".env"


class Settings(BaseSettings):
    app_name: str = "Viewers Leaderboard Backend"
    env: str = "dev"
    app_client_id: str
    app_client_secret: str
    app_access_token: str
    webhook_secret: str
    mongo_conn_str: str
    mongo_db_name: str

    model_config = SettingsConfigDict(env_file=get_env_filename())


@lru_cache
def get_settings():
    return Settings()

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    app_name: str = "Viewers Leaderboard Backend"
    client_id: str
    client_secret: str
    mongo_conn_str: str
    mongo_db_name: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Config:
    return Config()

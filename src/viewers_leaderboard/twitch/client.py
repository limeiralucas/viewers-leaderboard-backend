from twitchio import Client
from src.viewers_leaderboard.settings import get_settings


def get_twitch_client():
    settings = get_settings()

    return Client(
        token=settings.app_access_token,
        client_secret=settings.app_client_secret,
    )

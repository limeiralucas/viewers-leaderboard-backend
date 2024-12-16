from twitchio import Client
from src.viewers_leaderboard.settings import get_settings


def get_twitch_client():
    settings = get_settings()

    return Client.from_client_credentials(
        client_id=settings.app_client_id,
        client_secret=settings.app_client_secret,
    )

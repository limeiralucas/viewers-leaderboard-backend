from src.viewers_leaderboard.twitch.client import get_twitch_client


async def fetch_current_broadcaster_stream(broadcaster_username: str):
    client = get_twitch_client()
    streams = await client.fetch_streams(user_logins=[broadcaster_username])

    if len(streams) == 1:
        return streams[0]

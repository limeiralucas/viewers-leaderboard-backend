from hashlib import sha256
from twitchio.models import Stream
from src.viewers_leaderboard.twitch.client import get_twitch_client


async def fetch_current_broadcaster_stream(broadcaster_username: str):
    client = get_twitch_client()
    streams = await client.fetch_streams(user_logins=[broadcaster_username])

    if len(streams) == 1:
        return streams[0]


def gen_stream_hash(stream: Stream):
    username_timestamp = "_".join(
        [str(stream.user.id), str(stream.started_at)]
    ).encode()
    return sha256(username_timestamp).hexdigest()

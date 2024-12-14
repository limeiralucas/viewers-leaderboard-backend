from hashlib import sha256
from src.viewers_leaderboard.twitch.client import get_twitch_client
from src.viewers_leaderboard.twitch.models import TwitchStream


async def fetch_current_broadcaster_stream(broadcaster_id: str):
    client = get_twitch_client()
    streams = await client.fetch_streams(user_ids=[broadcaster_id])

    if len(streams) == 1:
        return TwitchStream.from_twitchio_stream(streams[0])


def gen_stream_hash(stream: TwitchStream):
    username_timestamp = "_".join(
        [stream.broadcaster_id, str(stream.started_at)]
    ).encode()
    return sha256(username_timestamp).hexdigest()

from datetime import datetime
from unittest.mock import patch, Mock, MagicMock, AsyncMock
import pytest
from twitchio import Stream
from polyfactory.pytest_plugin import register_fixture
from polyfactory.factories.pydantic_factory import ModelFactory
from src.viewers_leaderboard.twitch.stream import (
    fetch_current_broadcaster_stream,
    gen_stream_hash,
)
from src.viewers_leaderboard.twitch.models import TwitchStream


@register_fixture
class TwitchStreamFactory(ModelFactory[TwitchStream]): ...


@pytest.fixture
def stream_mock():
    data = {
        "id": "12345",
        "user_id": "123",
        "user_name": "test_user",
        "game_id": "123",
        "game_name": "Test Game",
        "type": "live",
        "title": "Test Stream",
        "viewer_count": 100,
        "started_at": "2023-01-01T00:00:00Z",
        "language": "en",
        "thumbnail_url": "http://example.com/thumbnail.jpg",
        "tags": ["tag1", "tag2"],
        "tag_ids": ["123", "123"],
        "is_mature": False,
    }
    yield Stream(http="TwitchHTTP", data=data)


@patch("src.viewers_leaderboard.twitch.stream.get_twitch_client")
async def test_fetch_current_broadcaster_stream_should_return_active_stream(
    mock_get_twitch_client: Mock,
    stream_mock: Stream,
):
    client = MagicMock()
    client.fetch_streams = AsyncMock(return_value=[stream_mock])
    mock_get_twitch_client.return_value = client

    result = await fetch_current_broadcaster_stream("test_user_id")

    assert result == TwitchStream.from_twitchio_stream(stream_mock)
    client.fetch_streams.assert_awaited_with(user_ids=["test_user_id"])


def test_gen_stream_hash_should_return_hash(twitch_stream_factory: TwitchStreamFactory):
    now = datetime.now()
    stream_mock: TwitchStream = twitch_stream_factory.build(
        broadcaster_id="1", started_at=now
    )

    expected_hash = "0a6c0e3b3e5b4d5b6f"
    expected_hash_arg = "_".join(
        [stream_mock.broadcaster_id, str(stream_mock.started_at)]
    ).encode()

    with patch("src.viewers_leaderboard.twitch.stream.sha256") as mock_sha256:
        mock_sha256.return_value.hexdigest.return_value = expected_hash

        result = gen_stream_hash(stream_mock)
        mock_sha256.assert_called_once_with(expected_hash_arg)

    assert result == expected_hash

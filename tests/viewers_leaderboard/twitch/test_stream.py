from datetime import datetime
from unittest.mock import patch, Mock, MagicMock, AsyncMock
from twitchio import Stream
from src.viewers_leaderboard.twitch.stream import (
    fetch_current_broadcaster_stream,
    gen_stream_hash,
)


@patch("src.viewers_leaderboard.twitch.stream.get_twitch_client")
async def test_fetch_current_broadcaster_stream_should_return_active_stream(
    mock_get_twitch_client: Mock,
    stream_mock: Stream,
):
    client = MagicMock()
    client.fetch_streams = AsyncMock(return_value=[stream_mock])
    mock_get_twitch_client.return_value = client

    result = await fetch_current_broadcaster_stream("test_user_id")

    assert result == stream_mock
    client.fetch_streams.assert_awaited_with(user_ids=["test_user_id"])


def test_gen_stream_hash_should_return_hash(stream_mock: Stream):
    now = datetime.now()

    stream_mock.user.id = 1
    stream_mock.started_at = now

    expected_hash = "0a6c0e3b3e5b4d5b6f"
    expected_hash_arg = "_".join(
        [str(stream_mock.user.id), str(stream_mock.started_at)]
    ).encode()

    with patch("src.viewers_leaderboard.twitch.stream.sha256") as mock_sha256:
        mock_sha256.return_value.hexdigest.return_value = expected_hash

        result = gen_stream_hash(stream_mock)
        mock_sha256.assert_called_once_with(expected_hash_arg)

    assert result == expected_hash

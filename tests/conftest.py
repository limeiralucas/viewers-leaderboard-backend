import pytest
from unittest.mock import patch
from twitchio import Stream
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture(autouse=True, scope="session")
def mock_db_client():
    with patch(
        "src.viewers_leaderboard.database.AsyncIOMotorClient", AsyncMongoMockClient
    ) as mocked_client:
        yield mocked_client


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

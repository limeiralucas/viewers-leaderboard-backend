from unittest.mock import patch
import pytest
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture(autouse=True, scope="session")
def mock_db_client():
    with patch(
        "src.viewers_leaderboard.database.AsyncIOMotorClient", AsyncMongoMockClient
    ) as mocked_client:
        yield mocked_client

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.viewers_leaderboard.main import app


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.mark.asyncio
@patch("src.viewers_leaderboard.ranking.routes.Score.aggregate")
async def test_ranking_route_should_return_channel_ranking(
    mock_aggregate: AsyncMock, test_client: TestClient
):
    mock_aggregate.return_value.to_list = AsyncMock(
        return_value=[
            {"username": "user1", "score": 10},
            {"username": "user2", "score": 5},
        ]
    )

    response = test_client.get("/ranking/test_channel")

    assert response.status_code == 200
    assert response.json() == [
        {"username": "user1", "score": 10},
        {"username": "user2", "score": 5},
    ]

    mock_aggregate.assert_called_once_with(
        [
            {"$match": {"broadcaster_user_id": "test_channel"}},
            {
                "$group": {
                    "_id": "$viewer_username",
                    "total_score": {"$sum": "$value"},
                }
            },
            {"$sort": {"total_score": -1}},
            {"$project": {"_id": 0, "username": "$_id", "score": "$total_score"}},
        ]
    )

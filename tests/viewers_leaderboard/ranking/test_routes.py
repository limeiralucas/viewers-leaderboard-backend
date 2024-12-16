from unittest.mock import patch, AsyncMock
import pytest
from polyfactory.pytest_plugin import register_fixture
from polyfactory.factories.pydantic_factory import ModelFactory
from fastapi.testclient import TestClient
from src.viewers_leaderboard.twitch.models import TwitchUser
from src.viewers_leaderboard.main import app


@register_fixture
class TwitchUserFactory(ModelFactory[TwitchUser]): ...


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.mark.asyncio
@patch("src.viewers_leaderboard.ranking.routes.get_user", new_callable=AsyncMock)
@patch("src.viewers_leaderboard.ranking.routes.Score.aggregate")
async def test_ranking_route_should_return_channel_ranking(
    mock_aggregate: AsyncMock,
    get_user_mock: AsyncMock,
    twitch_user_factory: TwitchUserFactory,
    test_client: TestClient,
):
    user_mocks: list[TwitchUser] = [twitch_user_factory.build() for _ in range(2)]

    def get_user_mock_side_effect(username: str):
        if username == "user1":
            return user_mocks[0]
        elif username == "user2":
            return user_mocks[1]
        return None

    get_user_mock.side_effect = get_user_mock_side_effect

    mock_aggregate.return_value.to_list = AsyncMock(
        return_value=[
            {
                "username": "user1",
                "score": 10,
                "profile_picture": user_mocks[0].profile_image,
            },
            {
                "username": "user2",
                "score": 5,
                "profile_picture": user_mocks[1].profile_image,
            },
        ]
    )

    response = test_client.get("/ranking/test_channel")

    assert response.status_code == 200
    assert response.json() == [
        {
            "username": "user1",
            "score": 10,
            "profile_picture": user_mocks[0].profile_image,
        },
        {
            "username": "user2",
            "score": 5,
            "profile_picture": user_mocks[1].profile_image,
        },
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

from unittest.mock import patch, AsyncMock
import pytest
from twitchio.models import Stream
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from src.viewers_leaderboard.main import app
from src.viewers_leaderboard.webhook.transport import (
    ChallengePayload,
    ChatMessagePayload,
)
from src.viewers_leaderboard.ranking.models import Score


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


@register_fixture
class ChallengePayloadFactory(ModelFactory[ChallengePayload]): ...


@register_fixture
class ChatMessagePayloadFactory(ModelFactory[ChatMessagePayload]): ...


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


def test_webhook_endpoint_should_answer_challenge(
    challenge_payload_factory: ChallengePayloadFactory,
    test_client: TestClient,
):
    payload: ChallengePayload = challenge_payload_factory.build()

    response = test_client.post(
        "/webhook",
        json=payload.model_dump(),
        headers={"twitch-eventsub-message-type": "webhook_callback_verification"},
    )

    assert response.status_code == 200
    assert response.headers.get("content-type") == "text/plain; charset=utf-8"
    assert response.text == payload.challenge


async def test_webhook_should_create_score_for_chat_if_doesnt_exist(
    chat_message_payload_factory: ChatMessagePayloadFactory,
    stream_mock: Stream,
    test_client: TestClient,
):
    payload: ChatMessagePayload = chat_message_payload_factory.build()

    with patch(
        "src.viewers_leaderboard.webhook.routes.fetch_current_broadcaster_stream",
        return_value=stream_mock,
    ):
        response = test_client.post(
            "/webhook",
            json=payload.model_dump(),
        )

    score = await Score.find_one()

    assert response.status_code == 200
    assert score.viewer_user_id == payload.event.chatter_user_id
    assert score.viewer_username == payload.event.chatter_user_name
    assert score.broadcaster_user_id == payload.event.broadcaster_user_id
    assert score.broadcaster_username == payload.event.broadcaster_user_name
    assert score.value == 1


async def test_webhook_should_increment_score_for_chat(
    chat_message_payload_factory: ChatMessagePayloadFactory,
    stream_mock: Stream,
    test_client: TestClient,
):
    payload: ChatMessagePayload = chat_message_payload_factory.build()

    with patch(
        "src.viewers_leaderboard.webhook.routes.fetch_current_broadcaster_stream",
        return_value=stream_mock,
    ):
        for _ in range(2):
            response = test_client.post(
                "/webhook",
                json=payload.model_dump(),
            )

    score = await Score.find_one()

    assert response.status_code == 200
    assert score.viewer_user_id == payload.event.chatter_user_id
    assert score.viewer_username == payload.event.chatter_user_name
    assert score.broadcaster_user_id == payload.event.broadcaster_user_id
    assert score.broadcaster_username == payload.event.broadcaster_user_name
    assert score.value == 2


@patch(
    "src.viewers_leaderboard.webhook.routes.fetch_current_broadcaster_stream",
    return_value=None,
)
async def test_webhook_should_ignore_chat_message_if_stream_is_offline(
    fetch_current_broadcaster_stream_mock: AsyncMock,
    chat_message_payload_factory: ChatMessagePayloadFactory,
    test_client: TestClient,
):
    payload: ChatMessagePayload = chat_message_payload_factory.build()

    response = test_client.post(
        "/webhook",
        json=payload.model_dump(),
    )

    score = await Score.find_one()

    fetch_current_broadcaster_stream_mock.assert_awaited_once_with(
        payload.event.broadcaster_user_name
    )
    assert response.status_code == 200
    assert score is None

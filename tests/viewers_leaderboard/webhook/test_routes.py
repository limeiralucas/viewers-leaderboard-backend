from datetime import datetime
from unittest.mock import patch, AsyncMock
import pytest
from freezegun import freeze_time
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


@pytest.mark.parametrize("elapsed_seconds,expected_score", [(300, 2), (2, 1)])
async def test_webhook_should_increment_score_for_chat_with_5_min_between_msgs(
    elapsed_seconds: int,
    expected_score: int,
    chat_message_payload_factory: ChatMessagePayloadFactory,
    stream_mock: Stream,
    test_client: TestClient,
):
    def receive_score():
        return test_client.post(
            "/webhook",
            json=payload.model_dump(),
        )

    payload: ChatMessagePayload = chat_message_payload_factory.build()

    with patch(
        "src.viewers_leaderboard.webhook.routes.fetch_current_broadcaster_stream",
        return_value=stream_mock,
    ):

        with freeze_time(datetime.now(), auto_tick_seconds=elapsed_seconds):
            # First message 5 minutes ago
            receive_score()

            # Second message now
            response = receive_score()

    score = await Score.find_one()

    assert response.status_code == 200
    assert score.viewer_user_id == payload.event.chatter_user_id
    assert score.viewer_username == payload.event.chatter_user_name
    assert score.broadcaster_user_id == payload.event.broadcaster_user_id
    assert score.broadcaster_username == payload.event.broadcaster_user_name
    assert score.value == expected_score


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

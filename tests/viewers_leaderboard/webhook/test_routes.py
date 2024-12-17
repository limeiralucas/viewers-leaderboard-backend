from urllib.parse import urlencode
from datetime import datetime
from unittest.mock import patch, AsyncMock, Mock
import pytest
from freezegun import freeze_time
from fastapi import HTTPException
from fastapi.testclient import TestClient
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from src.viewers_leaderboard.main import app
from src.viewers_leaderboard.webhook.transport import (
    ChallengePayload,
    ChatMessagePayload,
)
from src.viewers_leaderboard.ranking.models import Score
from src.viewers_leaderboard.twitch.models import TwitchStream
from src.viewers_leaderboard.twitch.auth import validate_webhook_request
from src.viewers_leaderboard.twitch.eventsub import WebhookSubscriptionConflictException
from src.viewers_leaderboard.settings import Settings


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        app.dependency_overrides[validate_webhook_request] = lambda: True
        yield client
        app.dependency_overrides = {}


@register_fixture
class ChallengePayloadFactory(ModelFactory[ChallengePayload]): ...


@register_fixture
class ChatMessagePayloadFactory(ModelFactory[ChatMessagePayload]): ...


@register_fixture
class TwitchStreamFactory(ModelFactory[TwitchStream]): ...


@register_fixture
class SettingsFactory(ModelFactory[Settings]): ...


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
    twitch_stream_factory: TwitchStreamFactory,
    test_client: TestClient,
):
    stream_mock: TwitchStream = twitch_stream_factory.build()
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
    assert score.value == 1


@pytest.mark.parametrize("elapsed_seconds,expected_score", [(300, 2), (2, 1)])
async def test_webhook_should_increment_score_for_chat_with_5_min_between_msgs(
    elapsed_seconds: int,
    expected_score: int,
    chat_message_payload_factory: ChatMessagePayloadFactory,
    twitch_stream_factory: TwitchStreamFactory,
    test_client: TestClient,
):
    def receive_score():
        return test_client.post(
            "/webhook",
            json=payload.model_dump(),
        )

    stream_mock: TwitchStream = twitch_stream_factory.build()
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
        payload.event.broadcaster_user_id
    )
    assert response.status_code == 200
    assert score is None


@patch(
    "src.viewers_leaderboard.webhook.routes.fetch_current_broadcaster_stream",
    return_value=None,
)
async def test_webhook_should_raise_http_error_403_if_validation_fails(
    fetch_current_broadcaster_stream_mock: AsyncMock,
    chat_message_payload_factory: ChatMessagePayloadFactory,
    test_client: TestClient,
):
    payload: ChatMessagePayload = chat_message_payload_factory.build()

    async def raise_403():
        raise HTTPException(status_code=403, detail="Invalid signature")

    test_client.app.dependency_overrides[validate_webhook_request] = raise_403

    response = test_client.post(
        "/webhook",
        json=payload.model_dump(),
    )

    assert response.status_code == 403
    fetch_current_broadcaster_stream_mock.assert_not_awaited()


@patch(
    "src.viewers_leaderboard.webhook.routes.fetch_current_broadcaster_stream",
    new_callable=AsyncMock,
)
async def test_webhook_should_use_active_stream_overrides_if_provided_and_env_is_dev(
    fetch_current_broadcaster_stream_mock: AsyncMock,
    chat_message_payload_factory: ChatMessagePayloadFactory,
    settings_factory: SettingsFactory,
    test_client: TestClient,
):
    settings = settings_factory.build(env="dev")
    payload: ChatMessagePayload = chat_message_payload_factory.build()
    headers = {
        "active-stream-broadcaster-id-override": "test_broadcaster_id",
        "active-stream-started-at-override": "2024-12-14T16:45:30",
    }

    with patch(
        "src.viewers_leaderboard.webhook.routes.get_settings", return_value=settings
    ):
        response = test_client.post(
            "/webhook",
            json=payload.model_dump(),
            headers=headers,
        )

    fetch_current_broadcaster_stream_mock.assert_not_awaited()

    score = await Score.find_one()

    assert response.status_code == 200
    assert score.viewer_user_id == payload.event.chatter_user_id
    assert score.viewer_username == payload.event.chatter_user_name
    assert score.broadcaster_user_id == payload.event.broadcaster_user_id
    assert score.value == 1


@patch("src.viewers_leaderboard.webhook.routes.get_settings")
async def test_webhook_subscribe_should_redirect_to_twitch_oauth(
    get_settings_mock: Mock,
    test_client: TestClient,
    settings_factory: SettingsFactory,
):
    mocked_settings = settings_factory.build()
    get_settings_mock.return_value = mocked_settings
    twitch_base_url = "https://id.twitch.tv/oauth2/authorize"

    query = urlencode(
        {
            "client_id": mocked_settings.app_client_id,
            "response_type": "code",
            "scope": "channel:bot user:bot user:read:chat",
            "redirect_uri": f"{mocked_settings.app_base_url}/webhook_subscribe_callback",
        }
    )

    expected_url = f"{twitch_base_url}?{query}"

    response = test_client.get("/webhook_subscribe", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == expected_url


@patch(
    "src.viewers_leaderboard.webhook.routes.subscribe_to_webhooks",
    new_callable=AsyncMock,
)
@patch(
    "src.viewers_leaderboard.webhook.routes.get_user_access_token",
    new_callable=AsyncMock,
)
async def test_webhook_subscribe_callback_should_subscribe_to_webhooks(
    get_user_access_token_mock: AsyncMock,
    subscribe_to_webhooks_mock: AsyncMock,
    test_client: TestClient,
):
    auth_code = "test-auth-code"
    access_token_response = get_user_access_token_mock.return_value

    response = test_client.get(f"/webhook_subscribe_callback?code={auth_code}")

    get_user_access_token_mock.assert_awaited_once_with(auth_code)
    subscribe_to_webhooks_mock.assert_awaited_once_with(
        access_token_response.access_token
    )

    assert response.status_code == 200
    assert response.text == "Application authorized!"


@patch(
    "src.viewers_leaderboard.webhook.routes.subscribe_to_webhooks",
    new_callable=AsyncMock,
)
@patch(
    "src.viewers_leaderboard.webhook.routes.get_user_access_token",
    new_callable=AsyncMock,
)
async def test_webhook_subscribe_callback_should_return_already_subscribed_message_if_conflict(
    get_user_access_token_mock: AsyncMock,
    subscribe_to_webhooks_mock: AsyncMock,
    test_client: TestClient,
):
    subscribe_to_webhooks_mock.side_effect = WebhookSubscriptionConflictException()
    response = test_client.get("/webhook_subscribe_callback?code=test-auth-code")

    assert response.status_code == 200
    assert response.text == "Already subscribed to webhook"

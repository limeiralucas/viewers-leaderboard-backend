from unittest.mock import AsyncMock, Mock, patch
import pytest
from twitchio.http import Route
from httpx import HTTPStatusError, Response
from pytest_httpx import HTTPXMock
from polyfactory.pytest_plugin import register_fixture
from polyfactory.factories.pydantic_factory import ModelFactory
from src.viewers_leaderboard.twitch.eventsub import (
    subscribe_to_webhooks,
    WebhookSubscriptionConflictException,
)
from src.viewers_leaderboard.settings import Settings
from src.viewers_leaderboard.twitch.transport import (
    AppTokenResponse,
    TokenValidationResponse,
)


@register_fixture
class SettingsFactory(ModelFactory[Settings]): ...


@register_fixture
class AppTokenResponseFactory(ModelFactory[AppTokenResponse]): ...


@register_fixture
class TokenValidationResponseFactory(ModelFactory[TokenValidationResponse]): ...


@patch("src.viewers_leaderboard.twitch.eventsub.get_settings")
@patch("src.viewers_leaderboard.twitch.eventsub.get_app_token", new_callable=AsyncMock)
@patch(
    "src.viewers_leaderboard.twitch.eventsub.validate_user_token",
    new_callable=AsyncMock,
)
async def test_subscribe_to_webhooks_should_make_request_for_webhook_subscription(
    mock_validate_user_token: AsyncMock,
    mock_get_app_token: AsyncMock,
    get_settings_mock: Mock,
    settings_factory: SettingsFactory,
    app_token_response_factory: AppTokenResponseFactory,
    token_validation_response_factory: TokenValidationResponseFactory,
    httpx_mock: HTTPXMock,
) -> None:
    app_token = "test-app-token"
    user_id = "test-user-id"

    mocked_settings = settings_factory.build()
    get_settings_mock.return_value = mocked_settings
    mock_get_app_token.return_value = app_token_response_factory.build(
        access_token=app_token
    )
    mock_validate_user_token.return_value = token_validation_response_factory.build(
        user_id=user_id
    )

    expected_request_data = {
        "type": "channel.chat.message",
        "version": 1,
        "condition": {
            "broadcaster_user_id": user_id,
            "user_id": user_id,
        },
        "transport": {
            "method": "webhook",
            "callback": f"{mocked_settings.app_base_url}/webhook",
            "secret": mocked_settings.webhook_secret,
        },
    }

    httpx_mock.add_response(
        method="POST",
        url=f"{Route.BASE_URL}/eventsub/subscriptions",
        match_json=expected_request_data,
        headers={
            "Client-ID": mocked_settings.app_client_id,
            "Authorization": f"Bearer {app_token}",
        },
    )

    await subscribe_to_webhooks("user_access_token")

    mock_get_app_token.assert_called_once()
    mock_validate_user_token.assert_called_once_with("user_access_token")


@patch("src.viewers_leaderboard.twitch.eventsub.get_settings")
@patch("src.viewers_leaderboard.twitch.eventsub.get_app_token", new_callable=AsyncMock)
@patch(
    "src.viewers_leaderboard.twitch.eventsub.validate_user_token",
    new_callable=AsyncMock,
)
async def test_subscribe_to_webhooks_should_raise_exception_if_webhook_already_subscribed(
    mock_validate_user_token: AsyncMock,
    mock_get_app_token: AsyncMock,
    get_settings_mock: Mock,
    settings_factory: SettingsFactory,
    app_token_response_factory: AppTokenResponseFactory,
    token_validation_response_factory: TokenValidationResponseFactory,
    httpx_mock: HTTPXMock,
) -> None:
    app_token = "test-app-token"
    user_id = "test-user-id"

    mocked_settings = settings_factory.build()
    get_settings_mock.return_value = mocked_settings
    mock_get_app_token.return_value = app_token_response_factory.build(
        access_token=app_token
    )
    mock_validate_user_token.return_value = token_validation_response_factory.build(
        user_id=user_id
    )

    httpx_mock.add_response(
        method="POST", url=f"{Route.BASE_URL}/eventsub/subscriptions", status_code=409
    )

    with pytest.raises(WebhookSubscriptionConflictException):
        await subscribe_to_webhooks("user_access_token")

    mock_get_app_token.assert_called_once()
    mock_validate_user_token.assert_called_once_with("user_access_token")

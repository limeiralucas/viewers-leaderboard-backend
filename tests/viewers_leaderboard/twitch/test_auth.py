import hmac
from hashlib import sha256
from unittest.mock import patch, AsyncMock, Mock
import pytest
from pytest_httpx import HTTPXMock
from polyfactory.pytest_plugin import register_fixture
from polyfactory.factories.pydantic_factory import ModelFactory
from fastapi import HTTPException
from fastapi.requests import Request
from src.viewers_leaderboard.twitch.auth import (
    validate_webhook_request,
    get_hmac_signature_from_request,
    get_user_access_token,
    validate_user_token,
    get_app_token,
)
from src.viewers_leaderboard.settings import Settings


@register_fixture
class SettingsFactory(ModelFactory[Settings]): ...


@pytest.fixture
def mock_request() -> Request:
    request = Mock(Request)
    request.headers = {
        "twitch-eventsub-message-signature": "sha256=valid_signature",
        "twitch-eventsub-message-id": "test_message_id",
        "twitch-eventsub-message-timestamp": "test_timestamp",
    }
    request.body = AsyncMock(return_value=b"test_body")
    return request


@patch(
    "src.viewers_leaderboard.twitch.auth.get_hmac_signature_from_request",
    new_callable=AsyncMock,
)
@patch("src.viewers_leaderboard.twitch.auth.get_settings")
async def test_validate_webhook_request_should_return_true_for_valid_signature(
    get_settings_mock: Mock,
    mock_get_hmac_signature_from_request: AsyncMock,
    mock_request: Request,
    settings_factory: SettingsFactory,
):
    get_settings_mock.return_value = settings_factory.build(
        twitch_signature_validation=True
    )
    mock_get_hmac_signature_from_request.return_value = "sha256=valid_signature"

    result = await validate_webhook_request(mock_request)

    assert result is True
    mock_get_hmac_signature_from_request.assert_called_once_with(mock_request)


@patch(
    "src.viewers_leaderboard.twitch.auth.get_hmac_signature_from_request",
    new_callable=AsyncMock,
)
@patch("src.viewers_leaderboard.twitch.auth.get_settings")
async def test_validate_webhook_request_should_raise_http_exception_403_for_invalid_signature(
    get_settings_mock: Mock,
    mock_get_hmac_signature_from_request: AsyncMock,
    mock_request: Request,
    settings_factory: SettingsFactory,
):
    get_settings_mock.return_value = settings_factory.build(
        twitch_signature_validation=True
    )
    mock_get_hmac_signature_from_request.return_value = "sha256=invalid_signature"

    with pytest.raises(HTTPException) as exc_info:
        await validate_webhook_request(mock_request)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Invalid signature"
    mock_get_hmac_signature_from_request.assert_called_once_with(mock_request)


@patch(
    "src.viewers_leaderboard.twitch.auth.get_hmac_signature_from_request",
    new_callable=AsyncMock,
)
@patch("src.viewers_leaderboard.twitch.auth.get_settings")
async def test_validate_webhook_request_signature_should_always_return_true_if_validation_is_disabled(
    get_settings_mock: Mock,
    mock_get_hmac_signature_from_request: AsyncMock,
    mock_request: Request,
    settings_factory: SettingsFactory,
):
    get_settings_mock.return_value = settings_factory.build(
        twitch_signature_validation=False
    )

    result = await validate_webhook_request(mock_request)

    assert result is True
    mock_get_hmac_signature_from_request.assert_not_called()


@patch("src.viewers_leaderboard.twitch.auth.get_settings")
async def test_get_hmac_signature_from_request_should_extract_signature_from_headers(
    get_settings_mock: Mock,
    mock_request: Request,
    settings_factory: SettingsFactory,
):
    get_settings_mock.return_value = settings_factory.build(
        webhook_secret="test_secret"
    )

    signature = await get_hmac_signature_from_request(mock_request)

    expected_data = "test_message_idtest_timestamptest_body"
    expected_signature = hmac.new(
        "test_secret".encode(), expected_data.encode(), digestmod=sha256
    ).hexdigest()
    expected_signature = f"sha256={expected_signature}"

    assert signature == expected_signature


@patch("src.viewers_leaderboard.twitch.auth.get_settings")
async def test_get_hmac_signature_from_request_should_return_type_error_for_missing_headers(
    get_settings_mock: Mock,
    mock_request: Request,
    settings_factory: SettingsFactory,
):
    get_settings_mock.return_value = settings_factory.build(
        webhook_secret="test_secret"
    )
    mock_request.headers = {}

    with pytest.raises(TypeError):
        await get_hmac_signature_from_request(mock_request)


@patch("src.viewers_leaderboard.twitch.auth.get_settings")
async def test_get_hmac_signature_from_request_should_return_type_error_for_invalid_body(
    get_settings_mock: Mock, mock_request: Request, settings_factory: SettingsFactory
):
    get_settings_mock.return_value = settings_factory.build(
        webhook_secret="test_secret"
    )
    mock_request.body = AsyncMock(return_value=None)

    with pytest.raises(AttributeError):
        await get_hmac_signature_from_request(mock_request)


@patch("src.viewers_leaderboard.twitch.auth.get_settings")
async def test_get_user_access_token_should_request_and_return_access_token(
    get_settings_mock: Mock,
    settings_factory: SettingsFactory,
    httpx_mock: HTTPXMock,
):
    mock_settings = settings_factory.build()
    get_settings_mock.return_value = mock_settings

    expected_request_data = {
        "client_id": mock_settings.app_client_id,
        "client_secret": mock_settings.app_client_secret,
        "code": "test_code",
        "grant_type": "authorization_code",
        "redirect_uri": f"{mock_settings.app_base_url}/webhook_subscribe_callback",
    }

    mock_response_data = {
        "access_token": "test_access_token",
        "expires_in": 3600,
        "refresh_token": "test_refresh_token",
        "scope": ["user:read:email"],
        "token_type": "bearer",
    }

    httpx_mock.add_response(
        method="POST",
        url="https://id.twitch.tv/oauth2/token",
        match_json=expected_request_data,
        json=mock_response_data,
    )

    result = await get_user_access_token("test_code")

    assert result.access_token == mock_response_data["access_token"]
    assert result.expires_in == mock_response_data["expires_in"]
    assert result.refresh_token == mock_response_data["refresh_token"]
    assert result.token_type == mock_response_data["token_type"]


async def test_validate_user_token_should_return_user_information(
    httpx_mock: HTTPXMock,
):
    mocked_response = {
        "client_id": "test-client-id",
        "login": "test-login",
        "scopes": ["user:read:email"],
        "user_id": "test-user-id",
        "expires_in": 3600,
    }
    httpx_mock.add_response(
        method="GET",
        url="https://id.twitch.tv/oauth2/validate",
        headers={"Authorization": "Bearer test-token"},
        json=mocked_response,
    )

    result = await validate_user_token("test-token")

    assert result.client_id == mocked_response["client_id"]
    assert result.login == mocked_response["login"]
    assert result.scopes == mocked_response["scopes"]
    assert result.user_id == mocked_response["user_id"]
    assert result.expires_in == mocked_response["expires_in"]


@patch("src.viewers_leaderboard.twitch.auth.get_settings")
async def test_get_app_token_should_request_and_return_app_token(
    get_settings_mock: Mock,
    settings_factory: SettingsFactory,
    httpx_mock: HTTPXMock,
):
    mocked_settings = settings_factory.build()
    get_settings_mock.return_value = mocked_settings

    expected_request_data = {
        "client_id": mocked_settings.app_client_id,
        "client_secret": mocked_settings.app_client_secret,
        "grant_type": "client_credentials",
    }

    mock_response_data = {
        "access_token": "test_access_token",
        "expires_in": 3600,
        "token_type": "bearer",
    }

    httpx_mock.add_response(
        method="POST",
        url="https://id.twitch.tv/oauth2/token",
        match_json=expected_request_data,
        json=mock_response_data,
    )

    result = await get_app_token()

    assert result.access_token == mock_response_data["access_token"]
    assert result.expires_in == mock_response_data["expires_in"]
    assert result.token_type == mock_response_data["token_type"]

from unittest.mock import patch, AsyncMock, Mock
import pytest
from twitchio import HTTPException
from twitchio.models import User
from src.viewers_leaderboard.twitch.user import (
    get_user,
    UserNotFoundException,
    AuthenticationError,
)


@pytest.fixture
def mocked_user() -> User:
    mocked_obj = Mock(
        spec=User,
        id=12345,
        profile_image="http://example.com/profile.jpg",
    )

    mocked_obj.name = "test_user"

    return mocked_obj


@pytest.fixture
def get_twitch_client_mock(mocked_user: User):
    def side_effect(names: list[str]):
        if names == [mocked_user.name]:
            return [mocked_user]
        return []

    mocked_get_users = AsyncMock(side_effect=side_effect)
    mocked_client = Mock(fetch_users=mocked_get_users)

    with patch("src.viewers_leaderboard.twitch.user.get_twitch_client") as mocked_get:
        mocked_get.return_value = mocked_client

        yield mocked_client


async def test_get_user_should_return_user_data(
    mocked_user: User,
    get_twitch_client_mock: Mock,
):
    user = await get_user(mocked_user.name)

    assert user.id == str(mocked_user.id)
    assert user.username == mocked_user.name
    assert user.profile_image == mocked_user.profile_image


async def test_get_user_should_raise_user_not_found_for_empty_result(
    get_twitch_client_mock: Mock,
):
    with pytest.raises(UserNotFoundException) as exc_info:
        await get_user("nonexistent_user")

    assert str(exc_info.value) == "User nonexistent_user not found"


async def test_get_user_should_raise_user_not_found_for_http_error(
    get_twitch_client_mock: Mock,
):
    get_twitch_client_mock.fetch_users.side_effect = HTTPException("API error")
    with pytest.raises(UserNotFoundException) as exc_info:
        await get_user("nonexistent_user")

    assert str(exc_info.value) == "User nonexistent_user not found"


async def test_get_user_should_raise_user_not_found_for_authentication_error(
    get_twitch_client_mock: Mock,
):
    get_twitch_client_mock.fetch_users.side_effect = AuthenticationError("API error")
    with pytest.raises(UserNotFoundException) as exc_info:
        await get_user("nonexistent_user")

    assert str(exc_info.value) == "User nonexistent_user not found"

from twitchio import HTTPException, AuthenticationError
from src.viewers_leaderboard.log import logger
from src.viewers_leaderboard.twitch.client import get_twitch_client
from src.viewers_leaderboard.twitch.models import TwitchUser


class UserNotFoundException(Exception): ...


async def get_user(username: str):
    try:
        client = get_twitch_client()
        users = await client.fetch_users(names=[username])

        if len(users) == 1:
            user = users[0]

            return TwitchUser(
                id=str(user.id), username=user.name, profile_image=user.profile_image
            )

        raise UserNotFoundException(f"User {username} not found")
    except (HTTPException, AuthenticationError) as ex:
        logger.error(f"Error fetching user {username}: {ex}")
        raise UserNotFoundException(f"User {username} not found") from ex

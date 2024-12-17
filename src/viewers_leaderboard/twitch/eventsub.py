from httpx import AsyncClient, HTTPStatusError
from twitchio.http import Route
from src.viewers_leaderboard.settings import get_settings
from src.viewers_leaderboard.twitch.auth import validate_user_token, get_app_token
from src.viewers_leaderboard.log import logger


class WebhookSubscriptionConflictException(Exception): ...


async def subscribe_to_webhooks(user_access_token: str):
    settings = get_settings()
    app_token_response = await get_app_token()
    token_validation = await validate_user_token(user_access_token)

    data = {
        "type": "channel.chat.message",
        "version": 1,
        "condition": {
            "broadcaster_user_id": token_validation.user_id,
            "user_id": token_validation.user_id,
        },
        "transport": {
            "method": "webhook",
            "callback": f"{settings.app_base_url}/webhook",
            "secret": settings.webhook_secret,
        },
    }

    url = f"{Route.BASE_URL}/eventsub/subscriptions"
    async with AsyncClient() as http_client:
        response = await http_client.post(
            url=url,
            json=data,
            headers={
                "Client-ID": settings.app_client_id,
                "Authorization": f"Bearer {app_token_response.access_token}",
                "Content-Type": "application/json",
            },
        )

    try:
        response.raise_for_status()
    except HTTPStatusError as ex:
        if ex.response.status_code == 409:
            logger.error("Already subscribed to webhook")
            raise WebhookSubscriptionConflictException() from ex
        raise ex

import hmac
from hashlib import sha256
from httpx import AsyncClient
from cachetools import TTLCache, cached
from fastapi import Request
from fastapi.exceptions import HTTPException
from src.viewers_leaderboard.log import logger
from src.viewers_leaderboard.settings import get_settings
from src.viewers_leaderboard.twitch.transport import (
    AuthUserTokenResponse,
    TokenValidationResponse,
    AppTokenResponse,
)


async def validate_webhook_request(request: Request) -> bool:
    if get_settings().twitch_signature_validation is False:
        return True

    try:
        expected_signature = await get_hmac_signature_from_request(request)
        header_signature = request.headers.get("twitch-eventsub-message-signature")

        if header_signature == expected_signature:
            return True
    except (TypeError, AttributeError) as ex:
        logger.error(f"Error validating webhook request: {ex}")

    raise HTTPException(status_code=403, detail="Invalid signature")


async def get_hmac_signature_from_request(request: Request) -> str:
    settings = get_settings()
    key = settings.webhook_secret
    data = await get_hmac_data_from_request(request)

    signature = hmac.new(key.encode(), data.encode(), digestmod=sha256).hexdigest()

    return f"sha256={signature}"


async def get_hmac_data_from_request(request: Request):
    body = await request.body()
    message_id: str = request.headers.get("twitch-eventsub-message-id")
    message_timestamp: str = request.headers.get("twitch-eventsub-message-timestamp")

    return message_id + message_timestamp + body.decode()


async def get_user_access_token(code: str):
    settings = get_settings()
    async with AsyncClient() as http_client:
        data = {
            "client_id": settings.app_client_id,
            "client_secret": settings.app_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": f"{settings.app_base_url}/webhook_subscribe_callback",
        }
        response = await http_client.post(
            "https://id.twitch.tv/oauth2/token",
            json=data,
        )

        response.raise_for_status()

        return AuthUserTokenResponse.model_validate(response.json())


async def validate_user_token(token: str):
    async with AsyncClient() as http_client:
        response = await http_client.get(
            "https://id.twitch.tv/oauth2/validate",
            headers={"Authorization": f"Bearer {token}"},
        )

        response.raise_for_status()

        return TokenValidationResponse.model_validate(response.json())


@cached(cache=TTLCache(maxsize=1, ttl=3600))
async def get_app_token():
    settings = get_settings()
    data = {
        "client_id": settings.app_client_id,
        "client_secret": settings.app_client_secret,
        "grant_type": "client_credentials",
    }

    async with AsyncClient() as http_client:
        response = await http_client.post(
            "https://id.twitch.tv/oauth2/token",
            json=data,
        )

    response.raise_for_status()

    return AppTokenResponse.model_validate(response.json())

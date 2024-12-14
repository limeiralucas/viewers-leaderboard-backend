import hmac
from hashlib import sha256
from fastapi import Request
from fastapi.exceptions import HTTPException
from src.viewers_leaderboard.log import logger
from src.viewers_leaderboard.settings import get_settings


async def validate_webhook_request(request: Request) -> bool:
    try:
        expected_signature = await get_hmac_signature_from_request(request)
        header_signature = request.headers.get("twitch-eventsub-message-signature")

        if header_signature == expected_signature:
            return True
    except TypeError as ex:
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

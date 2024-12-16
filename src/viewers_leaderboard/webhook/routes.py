from datetime import datetime
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import PlainTextResponse, RedirectResponse
from src.viewers_leaderboard.settings import get_settings
from src.viewers_leaderboard.webhook.transport import (
    WebhookPayload,
    ChallengePayload,
    ChatMessagePayload,
    ChatMessageEvent,
)
from src.viewers_leaderboard.twitch.models import TwitchStream
from src.viewers_leaderboard.ranking.models import Score, ScoreType
from src.viewers_leaderboard.twitch.stream import (
    fetch_current_broadcaster_stream,
    gen_stream_hash,
)
from src.viewers_leaderboard.twitch.auth import validate_webhook_request
from src.viewers_leaderboard.webhook.transport import (
    parse_active_stream_override_header,
)
from src.viewers_leaderboard.twitch.auth import get_user_access_token
from src.viewers_leaderboard.twitch.eventsub import subscribe_to_webhooks

router = APIRouter()


@router.post("/webhook")
async def webhook(
    payload: WebhookPayload,
    active_stream_override: TwitchStream | None = Depends(
        parse_active_stream_override_header
    ),
    _=Depends(validate_webhook_request),
):
    if isinstance(payload, ChallengePayload):
        return PlainTextResponse(content=payload.challenge)
    elif isinstance(payload, ChatMessagePayload):
        await handle_chat_message_event(payload.event, active_stream_override)

    return {"status": "ok"}


@router.get("/webhook_subscribe")
async def webhook_subscribe(request: Request):
    settings = get_settings()
    twitch_base_url = "https://id.twitch.tv/oauth2/authorize"
    params = {
        "client_id": settings.app_client_id,
        "response_type": "code",
        "scopes": "channel:bot user:read:chat",
        "redirect_uri": f"{request.base_url}webhook_subscribe_callback"
    }
    query = "&".join([f"{field}={value}" for field, value in params.items()])

    oauth_url = f"{twitch_base_url}?{query}"

    return RedirectResponse(oauth_url, status_code=status.HTTP_303_SEE_OTHER)

@router.get("/webhook_subscribe_callback")
async def webhook_subscribe_callback(code: str, request: Request):
    token_response = await get_user_access_token(code, request.base_url)

    await subscribe_to_webhooks(token_response.access_token)

    return PlainTextResponse("Application authorized!")


async def handle_chat_message_event(
    event: ChatMessageEvent, active_stream_override: TwitchStream
):
    broadcaster_user_id = event.broadcaster_user_id
    viewer_username = event.chatter_user_name
    viewer_user_id = event.chatter_user_id

    if all([get_settings().env == "dev", active_stream_override]):
        current_stream = active_stream_override
    else:
        current_stream = await fetch_current_broadcaster_stream(broadcaster_user_id)

    if current_stream is None:
        return

    stream_hash = gen_stream_hash(current_stream)

    score = await Score.find_one(
        Score.viewer_user_id == viewer_user_id,
        Score.broadcaster_user_id == broadcaster_user_id,
        Score.type == ScoreType.CHAT,
        Score.last_stream_hash == stream_hash,
    )

    if score is None:
        score = await Score(
            viewer_username=viewer_username,
            viewer_user_id=viewer_user_id,
            broadcaster_user_id=broadcaster_user_id,
            type=ScoreType.CHAT,
            last_stream_hash=stream_hash,
            value=1,
        ).save()
    elif should_score(score):
        await score.inc({Score.value: 1})


def should_score(score: Score):
    now = datetime.now()

    # 5 minutes elapsed
    return (now - score.updated_at).total_seconds() >= 300

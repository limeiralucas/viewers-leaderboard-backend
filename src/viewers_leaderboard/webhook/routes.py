from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
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

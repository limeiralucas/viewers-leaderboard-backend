from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from src.viewers_leaderboard.webhook.transport import (
    WebhookPayload,
    ChallengePayload,
    ChatMessagePayload,
    ChatMessageEvent,
)
from src.viewers_leaderboard.ranking.models import Score, ScoreType

router = APIRouter()


@router.post("/webhook")
async def webhook(payload: WebhookPayload):
    if isinstance(payload, ChallengePayload):
        return PlainTextResponse(content=payload.challenge)
    elif isinstance(payload, ChatMessagePayload):
        await handle_chat_message_event(payload.event)

    return {"status": "ok"}


async def handle_chat_message_event(event: ChatMessageEvent):
    broadcaster_username = event.broadcaster_user_name
    broadcaster_user_id = event.broadcaster_user_id
    viewer_username = event.chatter_user_name
    viewer_user_id = event.chatter_user_id

    score = await Score.find_one(
        Score.viewer_user_id == viewer_user_id,
        Score.broadcaster_user_id == broadcaster_user_id,
        Score.type == ScoreType.CHAT,
    )

    if score is None:
        score = await Score(
            viewer_username=viewer_username,
            viewer_user_id=viewer_user_id,
            broadcaster_username=broadcaster_username,
            broadcaster_user_id=broadcaster_user_id,
            type=ScoreType.CHAT,
            last_stream_hash="test-hash",
            value=1,
        ).save()
    else:
        await score.inc({Score.value: 1})

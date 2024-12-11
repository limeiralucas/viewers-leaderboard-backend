from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from beanie.operators import Eq
from src.viewers_leaderboard.webhook.transport import WebhookPayload, ChallengePayload, ChatMessagePayload, ChatMessageEvent
from src.viewers_leaderboard.ranking.models import Score, ScoreOrigin, Stream

router = APIRouter()


@router.post("/webhook")
async def webhook(payload: WebhookPayload):
    if isinstance(payload, ChallengePayload):
        return PlainTextResponse(content=payload.challenge)
    elif isinstance(payload, ChatMessagePayload):
        handle_chat_message_event(payload.event)

    return {"status": "ok"}


async def handle_chat_message_event(event: ChatMessageEvent):
    broadcaster_id = event.broadcaster_user_id
    author_id = event.chatter_user_id

    if broadcaster_id != author_id:
        active_stream = await Stream.find_one(
            Stream.broadcaster_id == broadcaster_id,
            Eq(Stream.ended_at, None),
        )

        if active_stream:
            score = Score(
                stream=active_stream,
                broadcaster_id=broadcaster_id,
                user_id=author_id,
                origin=ScoreOrigin.chat,
                value=1,
            )

            await score.insert()

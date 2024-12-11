from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from beanie.operators import Eq
from src.viewers_leaderboard.log import logger
from src.viewers_leaderboard.webhook.models import WebhookPayload, WebhookEvent
from src.viewers_leaderboard.ranking.models import Score, ScoreOrigin, Stream

router = APIRouter()


@router.post("/webhook")
async def webhook(payload: WebhookPayload, request: Request):
    message_type = request.headers.get("twitch-eventsub-message-type")

    if message_type == "webhook_callback_verification":
        return PlainTextResponse(content=payload.challenge)

    logger.info(payload.model_dump_json())

    subscription_type = payload.subscription.type

    match subscription_type:
        case "channel.chat.message":
            await handle_chat_message_event(payload.event)
        case "stream.online":
            await handle_stream_online_event(payload.event)
        case "stream.offline":
            await handle_stream_offline_event(payload.event)

    return {"status": "ok"}


async def handle_chat_message_event(event: WebhookEvent):
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


async def handle_stream_online_event(event: WebhookEvent):
    broadcaster_id = event.broadcaster_user_id

    active_stream = await Stream.find_one(
        Stream.broadcaster_id == broadcaster_id,
        Eq(Stream.ended_at, None),
    )
    if active_stream:
        active_stream.ended_at = datetime.now()
        await active_stream.update()

    stream = Stream(broadcaster_id=broadcaster_id)

    await stream.insert()


async def handle_stream_offline_event(event: WebhookEvent):
    broadcaster_id = event.broadcaster_user_id
    active_stream = await Stream.find_one(
        Stream.broadcaster_id == broadcaster_id,
        Eq(Stream.ended_at, None),
    )

    if active_stream:
        await active_stream.set({Stream.ended_at: datetime.now()})

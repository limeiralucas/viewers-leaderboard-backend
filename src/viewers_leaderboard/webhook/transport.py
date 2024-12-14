from typing import Union, Literal, Annotated
from pydantic import BaseModel
from fastapi import Header, HTTPException
from src.viewers_leaderboard.log import logger
from src.viewers_leaderboard.twitch.models import TwitchStream


class WebhookSubscription(BaseModel):
    type: str


class ChatMessageWebhookSubscription(WebhookSubscription):
    type: Literal["channel.chat.message"]


class BaseWebhookPayload(BaseModel):
    subscription: WebhookSubscription


class ChatMessageEvent(BaseModel):
    broadcaster_user_id: str
    chatter_user_id: str
    chatter_user_name: str


class ChatMessagePayload(BaseWebhookPayload):
    subscription: ChatMessageWebhookSubscription
    event: ChatMessageEvent


class ChallengePayload(BaseWebhookPayload):
    challenge: str


WebhookPayload = Union[ChatMessagePayload, ChallengePayload]


def parse_active_stream_override_header(
    active_stream_broadcaster_id_override: Annotated[
        str | None,
        Header(description="Dev-only override for current stream data broadcaster_id"),
    ] = None,
    active_stream_started_at_override: Annotated[
        str | None,
        Header(
            description="Dev-only override for current stream data started_at",
            example="2024-12-14T16:45:30",
        ),
    ] = None,
) -> TwitchStream | None:
    if all([active_stream_broadcaster_id_override, active_stream_started_at_override]):
        try:
            return TwitchStream(
                broadcaster_id=active_stream_broadcaster_id_override,
                started_at=active_stream_started_at_override,
            )
        except Exception as ex:
            logger.error(f"Error parsing active stream overrides: {ex}")
            raise HTTPException(400, "Invalid active stream overrides") from ex
    return None

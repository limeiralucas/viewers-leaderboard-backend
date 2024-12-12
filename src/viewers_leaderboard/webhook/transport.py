from typing import Union, Literal
from pydantic import BaseModel, Field


class WebhookSubscription(BaseModel):
    id: str
    type: str
    status: str
    version: str
    cost: int
    condition: dict[str, str]
    created_at: str
    transport: dict[str, str] = Field(default_factory=dict)


class ChatMessageWebhookSubscription(WebhookSubscription):
    type: Literal["channel.chat.message"]


class BaseWebhookPayload(BaseModel):
    subscription: WebhookSubscription


class ChatMessageEvent(BaseModel):
    broadcaster_user_id: str
    broadcaster_user_name: str
    chatter_user_id: str
    chatter_user_name: str


class ChatMessagePayload(BaseWebhookPayload):
    subscription: ChatMessageWebhookSubscription
    event: ChatMessageEvent


class ChallengePayload(BaseWebhookPayload):
    challenge: str


WebhookPayload = Union[ChatMessagePayload, ChallengePayload]

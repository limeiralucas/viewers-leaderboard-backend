from typing import Union, Literal
from pydantic import BaseModel


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

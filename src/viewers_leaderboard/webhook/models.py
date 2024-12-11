from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field, ConfigDict


@dataclass
class WebhookEvent:
    model_config = ConfigDict(extra="ignore")

    broadcaster_user_id: str
    chatter_user_id: str
    chatter_user_name: str


@dataclass
class WebhookSubscription:
    id: str
    type: str
    status: str
    version: str
    cost: int
    condition: dict[str, str]
    created_at: str
    transport: dict[str, str] = Field(default_factory=dict)


class WebhookPayload(BaseModel):
    subscription: WebhookSubscription
    challenge: Optional[str] = None
    event: WebhookEvent = Field(default_factory=dict)

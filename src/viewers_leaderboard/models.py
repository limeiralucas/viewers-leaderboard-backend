from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field, ConfigDict

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
    challenge: Optional[str] = None

class WebhookPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    subscription: WebhookSubscription
    event: dict[str, str] = Field(default_factory=dict)

from enum import Enum
from typing import Optional
from datetime import datetime
from beanie import Document, Link
from pydantic import Field


class Stream(Document):
    broadcaster_id: str
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None


class ScoreOrigin(Enum):
    view = "view"
    chat = "chat"


class Score(Document):
    stream: Link[Stream]
    user_id: str
    origin: ScoreOrigin
    value: int
    created_at: datetime = Field(default_factory=datetime.now)

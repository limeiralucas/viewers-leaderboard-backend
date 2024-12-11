from enum import Enum
from datetime import datetime
from beanie import Document
from pydantic import Field


class ScoreOrigin(Enum):
    view = "view"
    chat = "chat"


class Score(Document):
    stream: str
    user_id: str
    origin: ScoreOrigin
    value: int
    created_at: datetime = Field(default_factory=datetime.now)

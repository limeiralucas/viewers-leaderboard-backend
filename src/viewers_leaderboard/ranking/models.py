from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class ScoreOrigin(Enum):
    view = "view"
    chat = "chat"


class Score(BaseModel):
    stream: str
    user_id: str
    origin: ScoreOrigin
    value: int
    created_at: datetime = Field(default_factory=datetime.now)

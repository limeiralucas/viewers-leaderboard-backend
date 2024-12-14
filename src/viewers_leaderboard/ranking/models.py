from enum import Enum
from beanie import Document
from src.viewers_leaderboard.mixins import TimestampMixin


class ScoreType(Enum):
    CHAT = "chat"
    VIEW = "view"


class Score(Document, TimestampMixin):
    viewer_user_id: str
    viewer_username: str
    broadcaster_user_id: str
    type: ScoreType
    last_stream_hash: str
    value: int = 0

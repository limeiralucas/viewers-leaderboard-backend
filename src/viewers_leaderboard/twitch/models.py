from json import loads
from datetime import datetime
from pydantic import BaseModel
from twitchio.models import Stream


class TwitchStream(BaseModel):
    broadcaster_id: str
    started_at: datetime

    @staticmethod
    def from_twitchio_stream(stream: Stream):
        return TwitchStream(
            broadcaster_id=str(stream.user.id), started_at=stream.started_at
        )

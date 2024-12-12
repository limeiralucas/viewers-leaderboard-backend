from datetime import datetime
from pydantic import BaseModel, Field
from beanie import before_event, Update, SaveChanges, Replace


class TimestampMixin(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @before_event(Update, SaveChanges, Replace)
    def set_updated_at(self):
        self.updated_at = datetime.now()

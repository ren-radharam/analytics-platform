from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, UUID4


class EventIn(BaseModel):
    event_name: str
    properties: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime | None = None


class EventBatch(BaseModel):
    events: list[EventIn]


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    event_name: str
    properties: dict[str, Any]
    timestamp: datetime

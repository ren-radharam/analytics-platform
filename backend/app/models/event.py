import uuid

from sqlalchemy import Column, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    event_name = Column(String(255), nullable=False, index=True)
    source = Column(String(50), default="api")
    properties = Column(JSONB, default=dict)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    organization = relationship("Organization", back_populates="events")

    __table_args__ = (
        Index("ix_events_org_timestamp", "org_id", "timestamp"),
        Index("ix_events_org_name", "org_id", "event_name"),
    )

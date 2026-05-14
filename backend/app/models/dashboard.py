import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Dashboard(Base, TimestampMixin):
    __tablename__ = "dashboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization = relationship("Organization", back_populates="dashboards")
    widgets = relationship("Widget", back_populates="dashboard", cascade="all, delete-orphan")


class Widget(Base, TimestampMixin):
    __tablename__ = "widgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id"), nullable=False)
    title = Column(String(255), nullable=False)
    widget_type = Column(String(50), nullable=False)
    config = Column(JSONB, default=dict)
    position = Column(JSONB, default=lambda: {"x": 0, "y": 0, "w": 6, "h": 4})
    query_config = Column(JSONB, default=dict)
    dashboard = relationship("Dashboard", back_populates="widgets")

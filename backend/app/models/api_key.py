import secrets
import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    prefix = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="api_keys")

    @staticmethod
    def generate() -> tuple[str, str]:
        """Returns (raw_key, prefix)"""
        raw = secrets.token_urlsafe(32)
        prefix = raw[:8]
        return raw, prefix

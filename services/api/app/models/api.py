from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class API(Base):
    __tablename__ = "apis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    base_url = Column(String(512), nullable=False)

    auth_config = Column(JSON, nullable=True)

    is_active = Column(Boolean, default = True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="apis")
    versions = relationship("APIVersion", back_populates="api", cascade="all, delete-orphan")
    rate_limits = relationship("RateLimit", back_populates="api", cascade="all, delete-orphan")
    usage_metrics = relationship("UsageMetric", back_populates="api", cascade="all, delete-orphan")
    webhook_subscriptions = relationship("WebhookSubscription", back_populates="api", cascade="all, delete-orphan")
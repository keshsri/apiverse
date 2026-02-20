from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class UsageMetric(Base):
    __tablename__ = "usage_metrics"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id"), nullable=False)

    endpoint = Column(String(512), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    api = relationship("API", back_populates="usage_metrics")

    __table_args__ = (
        Index('idx_api_timestamp', 'api_id', 'timestamp'),
        Index('idx_api_endpoint', 'api_id', 'endpoint')
    )
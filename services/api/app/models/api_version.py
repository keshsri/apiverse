from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class APIVersion(Base):
    __tablename__ = "api_versions"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id"), nullable=False)

    version = Column(String(50), nullable=False)
    schema_snapshot = Column(JSON, nullable=True)
    change_summary = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    api = relationship("API", back_populates="versions")
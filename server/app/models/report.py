# server/app/models/report.py

import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    business_category = Column(String, nullable=False)
    available_margin = Column(Float, nullable=False)
    location = Column(JSON, nullable=False)          # {village, block, district, state}
    calculator_result = Column(JSON, nullable=True)   # scheme + EMI output
    advisory_result = Column(JSON, nullable=True)     # SWOT/market/pricing output
    created_at = Column(DateTime(timezone=True), server_default=func.now())
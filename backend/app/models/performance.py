import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.models.base import Base

class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    review_period = Column(String, nullable=False) # e.g., "Q1 2024", "Monthly - Jan 2024"
    rating = Column(Float, nullable=False) # e.g., 4.5 out of 5
    
    kpis = Column(JSONB, default=list) # List of KPIs and their status/score
    goals = Column(JSONB, default=list) # List of goals for the next period
    comments = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

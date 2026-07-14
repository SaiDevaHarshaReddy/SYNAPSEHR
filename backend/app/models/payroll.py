import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.models.base import Base

class Payroll(Base):
    __tablename__ = "payroll"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    
    month = Column(Integer, nullable=False) # 1 to 12
    year = Column(Integer, nullable=False)
    
    base_salary = Column(Float, nullable=False)
    deductions = Column(JSONB, default=list) # List of deductions with amount and reason
    bonuses = Column(JSONB, default=list) # List of bonuses with amount and reason
    net_salary = Column(Float, nullable=False)
    
    status = Column(String, nullable=False, default="Draft") # Draft, Processing, Paid
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

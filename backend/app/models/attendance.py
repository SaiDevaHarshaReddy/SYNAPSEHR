import uuid
from datetime import date, datetime, time
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    
    date = Column(Date, nullable=False, default=date.today)
    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)
    
    status = Column(String, nullable=False, default="Present") # Present, Absent, Half Day, Late
    total_hours = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

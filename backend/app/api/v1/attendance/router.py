from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.dependencies import get_current_user, require_role, require_roles
from app.database.database import get_db
from app.schemas.response import SuccessResponse
from app.models.attendance import Attendance

router = APIRouter(prefix="/attendance", tags=["Attendance"])

class AttendanceResponse(BaseModel):
    id: UUID
    employee_id: UUID
    date: date
    check_in: Optional[time]
    check_out: Optional[time]
    status: str
    total_hours: Optional[float]
    
    class Config:
        orm_mode = True

@router.post("/check-in", response_model=SuccessResponse[AttendanceResponse])
async def check_in(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check in for the current day."""
    if "employee_id" not in current_user or not current_user["employee_id"]:
        raise HTTPException(status_code=403, detail="User is not an employee")
        
    employee_id = UUID(current_user["employee_id"])
    today = date.today()
    now_time = datetime.now().time()
    
    # Check if already checked in
    query = select(Attendance).where(Attendance.employee_id == employee_id, Attendance.date == today)
    result = await db.execute(query)
    attendance = result.scalar_one_or_none()
    
    if attendance:
        if attendance.check_in:
            raise HTTPException(status_code=400, detail="Already checked in today")
        attendance.check_in = now_time
    else:
        attendance = Attendance(
            employee_id=employee_id,
            date=today,
            check_in=now_time,
            status="Present"
        )
        db.add(attendance)
        
    await db.commit()
    await db.refresh(attendance)
    
    return SuccessResponse(message="Checked in successfully", data=attendance)


@router.post("/check-out", response_model=SuccessResponse[AttendanceResponse])
async def check_out(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check out for the current day."""
    if "employee_id" not in current_user or not current_user["employee_id"]:
        raise HTTPException(status_code=403, detail="User is not an employee")
        
    employee_id = UUID(current_user["employee_id"])
    today = date.today()
    now_time = datetime.now().time()
    
    # Find today's attendance record
    query = select(Attendance).where(Attendance.employee_id == employee_id, Attendance.date == today)
    result = await db.execute(query)
    attendance = result.scalar_one_or_none()
    
    if not attendance or not attendance.check_in:
        raise HTTPException(status_code=400, detail="Not checked in today")
        
    if attendance.check_out:
        raise HTTPException(status_code=400, detail="Already checked out today")
        
    attendance.check_out = now_time
    
    # Calculate total hours roughly (for demo purposes)
    check_in_dt = datetime.combine(today, attendance.check_in)
    check_out_dt = datetime.combine(today, attendance.check_out)
    diff = check_out_dt - check_in_dt
    attendance.total_hours = round(diff.total_seconds() / 3600, 2)
    
    await db.commit()
    await db.refresh(attendance)
    
    return SuccessResponse(message="Checked out successfully", data=attendance)


@router.get("/", response_model=SuccessResponse[List[AttendanceResponse]])
async def list_attendance(
    employee_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List attendance records."""
    query = select(Attendance)
    
    user_role = current_user.get("role", "")
    if user_role not in ["admin", "hr", "manager"]:
        if "employee_id" in current_user and current_user["employee_id"]:
            query = query.where(Attendance.employee_id == UUID(current_user["employee_id"]))
        else:
            return SuccessResponse(message="No records found", data=[])
    else:
        if employee_id:
            query = query.where(Attendance.employee_id == employee_id)
            
    if start_date:
        query = query.where(Attendance.date >= start_date)
    if end_date:
        query = query.where(Attendance.date <= end_date)
        
    query = query.order_by(Attendance.date.desc())
    result = await db.execute(query)
    records = result.scalars().all()
    
    return SuccessResponse(message="Attendance records retrieved", data=records)

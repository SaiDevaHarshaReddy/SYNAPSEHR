"""HR Tickets API routes."""

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.employee import Employee
from app.models.hr_ticket import HRTicket
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/hr-tickets", tags=["HR Tickets"])


class CreateTicketRequest(BaseModel):
    subject: str
    message: str


class ReplyTicketRequest(BaseModel):
    message: str


@router.post("")
async def create_ticket(
    request: CreateTicketRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new HR ticket."""
    user_id = uuid.UUID(current_user["user_id"])
    emp_query = select(Employee).where(Employee.user_id == user_id)
    emp = (await db.execute(emp_query)).scalar_one_or_none()
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    new_ticket = HRTicket(
        employee_id=emp.id,
        subject=request.subject,
        status="open",
        messages=[{
            "sender_id": str(user_id),
            "sender_name": f"{emp.first_name} {emp.last_name}",
            "text": request.message,
            "timestamp": datetime.now().isoformat(),
            "is_hr": False
        }]
    )
    
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    
    return SuccessResponse(message="Ticket created successfully", data={"id": new_ticket.id})


@router.get("")
async def list_tickets(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List HR tickets. Employees see their own, HR/Admin see all."""
    user_id = uuid.UUID(current_user["user_id"])
    user_role = current_user.get("role")
    
    query = select(HRTicket).options(selectinload(HRTicket.employee)).order_by(HRTicket.updated_at.desc())
    
    if user_role not in ["hr", "admin", "administrator"]:
        emp_query = select(Employee).where(Employee.user_id == user_id)
        emp = (await db.execute(emp_query)).scalar_one_or_none()
        if not emp:
            return SuccessResponse(message="No tickets found", data=[])
        query = query.where(HRTicket.employee_id == emp.id)
        
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    data = []
    for t in tickets:
        data.append({
            "id": t.id,
            "subject": t.subject,
            "status": t.status,
            "employee_name": f"{t.employee.first_name} {t.employee.last_name}" if t.employee else "Unknown",
            "employee_id": t.employee_id,
            "messages": t.messages or [],
            "created_at": t.created_at,
            "updated_at": t.updated_at
        })
        
    return SuccessResponse(message="Tickets retrieved", data=data)


@router.post("/{ticket_id}/reply")
async def reply_to_ticket(
    ticket_id: uuid.UUID,
    request: ReplyTicketRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reply to a ticket."""
    user_id = uuid.UUID(current_user["user_id"])
    user_role = current_user.get("role")
    
    query = select(HRTicket).where(HRTicket.id == ticket_id)
    ticket = (await db.execute(query)).scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    emp_query = select(Employee).where(Employee.user_id == user_id)
    emp = (await db.execute(emp_query)).scalar_one_or_none()
    sender_name = f"{emp.first_name} {emp.last_name}" if emp else "HR Admin"
    is_hr = user_role in ["hr", "admin", "administrator"]
    
    new_message = {
        "sender_id": str(user_id),
        "sender_name": sender_name,
        "text": request.message,
        "timestamp": datetime.now().isoformat(),
        "is_hr": is_hr
    }
    
    # SQLAlchemy requires explicit assignment or flag_modified for JSON updates
    current_messages = ticket.messages or []
    current_messages.append(new_message)
    ticket.messages = current_messages
    
    # SQLAlchemy might not detect in-place mutation of JSON array without flag_modified, but we re-assign.
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(ticket, "messages")
    
    await db.commit()
    
    return SuccessResponse(message="Reply added", data=new_message)

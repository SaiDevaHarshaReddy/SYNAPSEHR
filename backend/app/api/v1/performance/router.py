from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.dependencies import get_current_user, require_role, require_roles
from app.database.database import get_db
from app.schemas.response import SuccessResponse
from app.models.performance import PerformanceReview

router = APIRouter(prefix="/performance", tags=["Performance"])

class KPIModel(BaseModel):
    name: str
    target: str
    achieved: str
    score: float

class GoalModel(BaseModel):
    description: str
    deadline: str

class PerformanceReviewCreate(BaseModel):
    employee_id: UUID
    review_period: str
    rating: float
    kpis: List[KPIModel]
    goals: List[GoalModel]
    comments: Optional[str] = None

class PerformanceReviewResponse(BaseModel):
    id: UUID
    employee_id: UUID
    reviewer_id: Optional[UUID]
    review_period: str
    rating: float
    kpis: list
    goals: list
    comments: Optional[str]
    created_at: datetime
    
    class Config:
        orm_mode = True

@router.post("/", response_model=SuccessResponse[PerformanceReviewResponse])
async def create_performance_review(
    data: PerformanceReviewCreate,
    current_user: dict = Depends(require_roles("admin", "hr", "manager")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new performance review."""
    reviewer_id = UUID(current_user["id"])
    
    review = PerformanceReview(
        employee_id=data.employee_id,
        reviewer_id=reviewer_id,
        review_period=data.review_period,
        rating=data.rating,
        kpis=[k.dict() for k in data.kpis],
        goals=[g.dict() for g in data.goals],
        comments=data.comments
    )
    
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    return SuccessResponse(message="Performance review created successfully", data=review)


@router.get("/", response_model=SuccessResponse[List[PerformanceReviewResponse]])
async def list_performance_reviews(
    employee_id: Optional[UUID] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List performance reviews, optionally filtered by employee."""
    query = select(PerformanceReview)
    
    # Non-HR/Admin users can only see their own reviews
    user_role = current_user.get("role", "")
    if user_role not in ["admin", "hr", "manager"]:
        if "employee_id" in current_user:
            query = query.where(PerformanceReview.employee_id == UUID(current_user["employee_id"]))
        else:
            return SuccessResponse(message="No reviews found", data=[])
    else:
        if employee_id:
            query = query.where(PerformanceReview.employee_id == employee_id)
            
    query = query.order_by(PerformanceReview.created_at.desc())
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return SuccessResponse(message="Performance reviews retrieved", data=reviews)

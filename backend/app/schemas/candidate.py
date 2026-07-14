"""Candidate schemas for recruitment module."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class CandidateScoreRequest(BaseSchema):
    """Request to score a candidate against a job description."""

    job_title: str
    job_description: str


class InterviewQuestionsRequest(BaseSchema):
    """Request to generate interview questions."""

    job_title: Optional[str] = None
    experience_level: Optional[str] = None
    focus_skills: Optional[list[str]] = None


class CandidateStageUpdate(BaseSchema):
    """Update candidate hiring stage."""

    stage: str = Field(..., pattern="^(new|shortlisted|interview_scheduled|offer_sent|hired|rejected)$")


class CandidateResponse(BaseSchema):
    """Full candidate response."""

    id: UUID
    organization_id: UUID
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    current_role: Optional[str] = None
    years_of_experience: Optional[float] = None
    skills: list[str] = []
    education: list[dict] = []
    experience: list[dict] = []
    certifications: list[str] = []
    languages: list[str] = []
    projects: list[dict] = []
    job_title: Optional[str] = None
    overall_score: Optional[float] = None
    skill_match_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    recommendation: Optional[str] = None
    match_explanation: Optional[str] = None
    missing_skills: list[str] = []
    stage: str
    interview_questions: Any = None
    resume_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CandidateListResponse(BaseSchema):
    """Lightweight candidate listing."""

    id: UUID
    full_name: str
    email: Optional[str] = None
    current_role: Optional[str] = None
    years_of_experience: Optional[float] = None
    skills: list[str] = []
    overall_score: Optional[float] = None
    recommendation: Optional[str] = None
    match_explanation: Optional[str] = None
    stage: str
    job_title: Optional[str] = None
    created_at: datetime

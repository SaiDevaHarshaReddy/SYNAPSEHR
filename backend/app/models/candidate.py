"""Candidate model for recruitment module."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Candidate(BaseModel):
    """Represents a job candidate / resume submission."""

    __tablename__ = "candidates"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )

    # Basic info (parsed from resume)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Resume content
    resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Parsed structured data (stored as JSON strings)
    skills_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list of skills
    experience_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    education_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    certifications_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    languages_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    projects_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Experience summary
    years_of_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_role: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Job matching
    job_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    job_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    skill_match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    education_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Highly Recommended, Recommended, etc.
    missing_skills_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    match_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Hiring stage
    stage: Mapped[str] = mapped_column(
        String(50), nullable=False, default="new"
    )  # new, shortlisted, interview_scheduled, offer_sent, hired, rejected

    # Interview questions (JSON)
    interview_questions_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    organization = relationship("Organization", lazy="selectin")

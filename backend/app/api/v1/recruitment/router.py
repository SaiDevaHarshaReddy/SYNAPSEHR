"""Recruitment API routes – resume upload, candidate management, scoring and interview questions."""

import io
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_role
from app.database.database import get_db
from app.schemas.candidate import (
    CandidateListResponse,
    CandidateResponse,
    CandidateScoreRequest,
    CandidateStageUpdate,
    InterviewQuestionsRequest,
)
from app.schemas.response import SuccessResponse
from app.services.candidate import CandidateService

router = APIRouter(prefix="/recruitment", tags=["Recruitment"])


def _extract_text_from_upload(content: bytes, filename: str) -> str:
    """Extract plain text from uploaded file (PDF / DOCX / TXT)."""
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception:
            pass

        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            pass

    if filename_lower.endswith(".docx"):
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            pass

    # Fallback: try to decode as UTF-8 text
    try:
        return content.decode("utf-8", errors="replace")
    except Exception:
        return ""


@router.post("/upload", response_model=SuccessResponse[CandidateResponse])
async def upload_resume(
    file: UploadFile = File(...),
    job_title: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a resume (PDF/DOCX/TXT), parse with AI, and create candidate."""
    content = await file.read()
    resume_text = _extract_text_from_upload(content, file.filename or "resume.txt")

    if not resume_text.strip():
        resume_text = content.decode("utf-8", errors="replace")

    service = CandidateService(db)
    org_id_str = current_user.get("organization_id")
    org_uuid = UUID(org_id_str) if org_id_str else None
    
    if not org_uuid:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="User must belong to an organization to upload a resume")

    candidate = await service.parse_and_create_candidate(
        organization_id=org_uuid,
        resume_text=resume_text,
        filename=file.filename or "resume",
        job_title=job_title,
        job_description=job_description,
    )

    return SuccessResponse(message="Resume uploaded and parsed successfully", data=candidate)


@router.get("/candidates", response_model=SuccessResponse[list[CandidateListResponse]])
async def list_candidates(
    search: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List candidates with optional filters."""
    service = CandidateService(db)
    org_id = current_user.get("organization_id")
    org_uuid = UUID(org_id) if org_id else None
    candidates = await service.list_candidates(
        organization_id=org_uuid,
        search=search,
        stage=stage,
        min_score=min_score,
    )
    return SuccessResponse(message="Candidates retrieved", data=candidates)


@router.get("/candidates/{candidate_id}", response_model=SuccessResponse[CandidateResponse])
async def get_candidate(
    candidate_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single candidate's full details."""
    service = CandidateService(db)
    candidate = await service.get_candidate(candidate_id)
    return SuccessResponse(message="Candidate retrieved", data=candidate)


@router.post("/candidates/{candidate_id}/score", response_model=SuccessResponse[CandidateResponse])
async def score_candidate(
    candidate_id: UUID,
    data: CandidateScoreRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Score a candidate against a job description."""
    service = CandidateService(db)
    candidate = await service.score_candidate(candidate_id, data.job_title, data.job_description)
    return SuccessResponse(message="Candidate scored", data=candidate)


@router.post(
    "/candidates/{candidate_id}/interview-questions",
    response_model=SuccessResponse[CandidateResponse],
)
async def generate_interview_questions(
    candidate_id: UUID,
    data: InterviewQuestionsRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate AI-powered interview questions for a candidate."""
    service = CandidateService(db)
    candidate = await service.generate_interview_questions(
        candidate_id=candidate_id,
        job_title=data.job_title,
        focus_skills=data.focus_skills,
    )
    return SuccessResponse(message="Interview questions generated", data=candidate)


@router.patch("/candidates/{candidate_id}/stage", response_model=SuccessResponse[CandidateResponse])
async def update_candidate_stage(
    candidate_id: UUID,
    data: CandidateStageUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update candidate's hiring stage."""
    service = CandidateService(db)
    candidate = await service.update_stage(candidate_id, data.stage)
    return SuccessResponse(message=f"Candidate stage updated to {data.stage}", data=candidate)


@router.delete("/candidates/{candidate_id}", response_model=SuccessResponse[dict])
async def delete_candidate(
    candidate_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a candidate."""
    service = CandidateService(db)
    await service.delete_candidate(candidate_id)
    return SuccessResponse(message="Candidate deleted", data={})


@router.get("/stats", response_model=SuccessResponse[dict])
async def get_recruitment_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recruitment dashboard statistics."""
    from sqlalchemy import func, select
    from app.models.candidate import Candidate

    org_id_str = current_user.get("organization_id")
    org_id = UUID(org_id_str) if org_id_str else None

    def apply_filters(q):
        if org_id:
            q = q.where(Candidate.organization_id == org_id)
        if start_date:
            q = q.where(Candidate.created_at >= start_date)
        if end_date:
            q = q.where(Candidate.created_at <= end_date)
        return q

    total_query = apply_filters(select(func.count()).select_from(Candidate))
    total = (await db.execute(total_query)).scalar() or 0

    shortlisted_query = apply_filters(select(func.count()).select_from(Candidate).where(Candidate.stage == "shortlisted"))
    shortlisted = (await db.execute(shortlisted_query)).scalar() or 0

    interviews_query = apply_filters(select(func.count()).select_from(Candidate).where(Candidate.stage == "interview_scheduled"))
    interviews = (await db.execute(interviews_query)).scalar() or 0

    hired_query = apply_filters(select(func.count()).select_from(Candidate).where(Candidate.stage == "hired"))
    hired = (await db.execute(hired_query)).scalar() or 0

    # Stage distribution
    stage_query = apply_filters(select(Candidate.stage, func.count()).group_by(Candidate.stage))
    stage_result = await db.execute(stage_query)
    stage_counts = dict(stage_result.all())

    # Average score
    avg_score_query = apply_filters(select(func.avg(Candidate.overall_score)).where(Candidate.overall_score.isnot(None)))
    avg_score_result = await db.execute(avg_score_query)
    avg_score = round(avg_score_result.scalar() or 0, 1)

    return SuccessResponse(
        message="Recruitment stats retrieved",
        data={
            "total_candidates": total,
            "shortlisted": shortlisted,
            "interviews_scheduled": interviews,
            "hired": hired,
            "average_score": avg_score,
            "stage_distribution": stage_counts,
        },
    )

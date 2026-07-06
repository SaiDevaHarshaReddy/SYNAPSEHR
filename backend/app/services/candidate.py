"""Candidate service – resume parsing, scoring and interview question generation."""

import json
import re
from typing import Optional
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.schemas.candidate import CandidateListResponse, CandidateResponse

logger = structlog.get_logger()


def _parse_json_field(value: Optional[str]) -> list:
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []


def _to_response(c: Candidate) -> CandidateResponse:
    return CandidateResponse(
        id=c.id,
        organization_id=c.organization_id,
        full_name=c.full_name,
        email=c.email,
        phone=c.phone,
        current_role=c.current_role,
        years_of_experience=c.years_of_experience,
        skills=_parse_json_field(c.skills_json),
        education=_parse_json_field(c.education_json),
        experience=_parse_json_field(c.experience_json),
        certifications=_parse_json_field(c.certifications_json),
        languages=_parse_json_field(c.languages_json),
        projects=_parse_json_field(c.projects_json),
        job_title=c.job_title,
        overall_score=c.overall_score,
        skill_match_score=c.skill_match_score,
        experience_score=c.experience_score,
        education_score=c.education_score,
        recommendation=c.recommendation,
        missing_skills=_parse_json_field(c.missing_skills_json),
        stage=c.stage,
        interview_questions=_parse_json_field(c.interview_questions_json),
        resume_filename=c.resume_filename,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


def _to_list_response(c: Candidate) -> CandidateListResponse:
    return CandidateListResponse(
        id=c.id,
        full_name=c.full_name,
        email=c.email,
        current_role=c.current_role,
        years_of_experience=c.years_of_experience,
        skills=_parse_json_field(c.skills_json),
        overall_score=c.overall_score,
        recommendation=c.recommendation,
        stage=c.stage,
        job_title=c.job_title,
        created_at=c.created_at,
    )


class CandidateService:
    """Handles AI-powered resume parsing, scoring and interview question generation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def parse_and_create_candidate(
        self,
        organization_id: UUID,
        resume_text: str,
        filename: str,
        job_title: Optional[str] = None,
        job_description: Optional[str] = None,
    ) -> CandidateResponse:
        """Parse resume text with AI and store as candidate."""
        parsed = await self._ai_parse_resume(resume_text)

        candidate = Candidate(
            organization_id=organization_id,
            full_name=parsed.get("full_name", "Unknown Candidate"),
            email=parsed.get("email"),
            phone=parsed.get("phone"),
            resume_text=resume_text,
            resume_filename=filename,
            current_role=parsed.get("current_role"),
            years_of_experience=parsed.get("years_of_experience"),
            skills_json=json.dumps(parsed.get("skills", [])),
            experience_json=json.dumps(parsed.get("experience", [])),
            education_json=json.dumps(parsed.get("education", [])),
            certifications_json=json.dumps(parsed.get("certifications", [])),
            languages_json=json.dumps(parsed.get("languages", [])),
            projects_json=json.dumps(parsed.get("projects", [])),
            job_title=job_title,
            job_description=job_description,
            stage="new",
        )

        # Score immediately if JD provided
        if job_description:
            score_data = await self._ai_score_candidate(
                parsed, job_title or "Position", job_description
            )
            candidate.overall_score = score_data.get("overall_score")
            candidate.skill_match_score = score_data.get("skill_match_score")
            candidate.experience_score = score_data.get("experience_score")
            candidate.education_score = score_data.get("education_score")
            candidate.recommendation = score_data.get("recommendation")
            candidate.missing_skills_json = json.dumps(score_data.get("missing_skills", []))

        self.session.add(candidate)
        await self.session.commit()
        await self.session.refresh(candidate)

        logger.info("candidate_created", candidate_id=str(candidate.id), name=candidate.full_name)
        return _to_response(candidate)

    async def score_candidate(
        self, candidate_id: UUID, job_title: str, job_description: str
    ) -> CandidateResponse:
        """Score an existing candidate against a job description."""
        result = await self.session.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        if candidate is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Candidate", str(candidate_id))

        parsed = {
            "skills": _parse_json_field(candidate.skills_json),
            "experience": _parse_json_field(candidate.experience_json),
            "education": _parse_json_field(candidate.education_json),
            "years_of_experience": candidate.years_of_experience or 0,
        }

        score_data = await self._ai_score_candidate(parsed, job_title, job_description)

        candidate.job_title = job_title
        candidate.job_description = job_description
        candidate.overall_score = score_data.get("overall_score")
        candidate.skill_match_score = score_data.get("skill_match_score")
        candidate.experience_score = score_data.get("experience_score")
        candidate.education_score = score_data.get("education_score")
        candidate.recommendation = score_data.get("recommendation")
        candidate.missing_skills_json = json.dumps(score_data.get("missing_skills", []))

        await self.session.commit()
        await self.session.refresh(candidate)
        return _to_response(candidate)

    async def generate_interview_questions(
        self,
        candidate_id: UUID,
        job_title: Optional[str] = None,
        focus_skills: Optional[list[str]] = None,
    ) -> CandidateResponse:
        """Generate personalized interview questions for a candidate."""
        result = await self.session.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        if candidate is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Candidate", str(candidate_id))

        skills = focus_skills or _parse_json_field(candidate.skills_json)[:8]
        jt = job_title or candidate.job_title or "Software Developer"

        questions = await self._ai_generate_interview_questions(jt, skills, candidate.resume_text or "")

        candidate.interview_questions_json = json.dumps(questions)
        await self.session.commit()
        await self.session.refresh(candidate)
        return _to_response(candidate)

    async def list_candidates(
        self,
        organization_id: Optional[UUID] = None,
        search: Optional[str] = None,
        stage: Optional[str] = None,
        min_score: Optional[float] = None,
    ) -> list[CandidateListResponse]:
        """List candidates with optional filters."""
        query = select(Candidate)
        if organization_id:
            query = query.where(Candidate.organization_id == organization_id)

        if stage:
            query = query.where(Candidate.stage == stage)
        if min_score is not None:
            query = query.where(Candidate.overall_score >= min_score)

        query = query.order_by(Candidate.created_at.desc())
        result = await self.session.execute(query)
        candidates = result.scalars().all()

        if search:
            search_lower = search.lower()
            candidates = [
                c for c in candidates
                if search_lower in c.full_name.lower()
                or (c.email and search_lower in c.email.lower())
                or (c.current_role and search_lower in c.current_role.lower())
                or any(search_lower in s.lower() for s in _parse_json_field(c.skills_json))
            ]

        return [_to_list_response(c) for c in candidates]

    async def get_candidate(self, candidate_id: UUID) -> CandidateResponse:
        """Get a single candidate by ID."""
        result = await self.session.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        if candidate is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Candidate", str(candidate_id))
        return _to_response(candidate)

    async def update_stage(self, candidate_id: UUID, stage: str) -> CandidateResponse:
        """Update candidate hiring stage."""
        result = await self.session.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        if candidate is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("Candidate", str(candidate_id))

        candidate.stage = stage
        await self.session.commit()
        await self.session.refresh(candidate)
        return _to_response(candidate)

    async def delete_candidate(self, candidate_id: UUID) -> None:
        """Delete a candidate."""
        result = await self.session.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        if candidate:
            await self.session.delete(candidate)
            await self.session.commit()

    # ───────────────────── AI Helpers ─────────────────────

    async def _ai_parse_resume(self, resume_text: str) -> dict:
        """Use AI to extract structured data from resume text."""
        prompt = f"""You are an expert resume parser. Extract structured information from the following resume text.

Return a JSON object with exactly these fields:
{{
  "full_name": "string",
  "email": "string or null",
  "phone": "string or null",
  "current_role": "most recent job title",
  "years_of_experience": number (float, total years),
  "skills": ["skill1", "skill2", ...],
  "experience": [
    {{"role": "...", "company": "...", "duration": "...", "description": "..."}}
  ],
  "education": [
    {{"degree": "...", "institution": "...", "year": "..."}}
  ],
  "certifications": ["cert1", "cert2"],
  "languages": ["English", ...],
  "projects": [
    {{"name": "...", "description": "...", "technologies": ["..."]}}
  ]
}}

Resume text:
{resume_text[:4000]}

Return ONLY the JSON object, no markdown, no explanation."""

        try:
            response_text = await self._call_ai(prompt)
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning("ai_parse_failed", error=str(e))

        # Fallback: extract basics with regex
        return self._regex_parse_resume(resume_text)

    def _regex_parse_resume(self, text: str) -> dict:
        """Fallback regex-based resume parser."""
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
        phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,15}', text)
        lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
        name = lines[0] if lines else "Unknown Candidate"

        # Extract skills by looking for common tech keywords
        common_skills = [
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI",
            "Django", "Flask", "SQL", "PostgreSQL", "MongoDB", "Docker",
            "Kubernetes", "AWS", "GCP", "Azure", "Machine Learning", "TensorFlow",
            "PyTorch", "Java", "C++", "C#", "Go", "Rust", "HTML", "CSS",
            "Vue", "Angular", "Redis", "Kafka", "Git", "Linux",
        ]
        found_skills = [s for s in common_skills if re.search(r'\b' + re.escape(s) + r'\b', text, re.IGNORECASE)]

        return {
            "full_name": name,
            "email": email_match.group() if email_match else None,
            "phone": phone_match.group().strip() if phone_match else None,
            "current_role": None,
            "years_of_experience": None,
            "skills": found_skills,
            "experience": [],
            "education": [],
            "certifications": [],
            "languages": ["English"],
            "projects": [],
        }

    async def _ai_score_candidate(
        self, parsed_resume: dict, job_title: str, job_description: str
    ) -> dict:
        """Score candidate against job description using AI."""
        prompt = f"""You are an expert HR recruiter. Score the following candidate against the job requirements.

Job Title: {job_title}
Job Description: {job_description[:2000]}

Candidate Profile:
- Skills: {', '.join(parsed_resume.get('skills', []))}
- Experience: {parsed_resume.get('years_of_experience', 0)} years
- Education: {json.dumps(parsed_resume.get('education', []))}
- Experience: {json.dumps(parsed_resume.get('experience', [])[:3])}

Return a JSON object:
{{
  "overall_score": <0-100>,
  "skill_match_score": <0-100>,
  "experience_score": <0-100>,
  "education_score": <0-100>,
  "recommendation": "Highly Recommended" | "Recommended" | "Consider" | "Not Recommended",
  "missing_skills": ["skill1", "skill2", ...]
}}

Return ONLY the JSON object."""

        try:
            response_text = await self._call_ai(prompt)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data
        except Exception as e:
            logger.warning("ai_score_failed", error=str(e))

        # Fallback scoring
        candidate_skills = set(s.lower() for s in parsed_resume.get("skills", []))
        jd_words = set(job_description.lower().split())
        overlap = len(candidate_skills & jd_words)
        skill_score = min(100, overlap * 10)
        exp = parsed_resume.get("years_of_experience") or 0
        exp_score = min(100, exp * 12)
        overall = round((skill_score * 0.5 + exp_score * 0.3 + 70 * 0.2), 1)

        rec = "Not Recommended"
        if overall >= 80:
            rec = "Highly Recommended"
        elif overall >= 65:
            rec = "Recommended"
        elif overall >= 45:
            rec = "Consider"

        return {
            "overall_score": overall,
            "skill_match_score": skill_score,
            "experience_score": exp_score,
            "education_score": 70.0,
            "recommendation": rec,
            "missing_skills": [],
        }

    async def _ai_generate_interview_questions(
        self, job_title: str, skills: list[str], resume_text: str
    ) -> list[dict]:
        """Generate personalized interview questions."""
        skills_str = ', '.join(skills[:10]) if skills else 'general software development'
        prompt = f"""You are an expert technical interviewer. Generate 10 personalized interview questions for a {job_title} candidate.

Candidate skills: {skills_str}

Create questions in these categories:
- Technical (based on their skills)
- Problem Solving  
- Behavioral
- System Design

Return a JSON array:
[
  {{"category": "Technical", "question": "...", "difficulty": "Easy|Medium|Hard"}},
  ...
]

Return ONLY the JSON array."""

        try:
            response_text = await self._call_ai(prompt)
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning("ai_questions_failed", error=str(e))

        # Fallback questions
        return self._generate_fallback_questions(job_title, skills)

    def _generate_fallback_questions(self, job_title: str, skills: list[str]) -> list[dict]:
        """Generate fallback interview questions."""
        tech_questions = []
        for skill in skills[:4]:
            tech_questions.append({
                "category": "Technical",
                "question": f"Can you explain your experience with {skill} and describe a project where you used it effectively?",
                "difficulty": "Medium"
            })

        return tech_questions + [
            {"category": "Technical", "question": f"What are the key principles you follow when building {job_title} solutions?", "difficulty": "Medium"},
            {"category": "Problem Solving", "question": "Describe a time when you faced a complex technical challenge. How did you approach solving it?", "difficulty": "Medium"},
            {"category": "Problem Solving", "question": "How do you debug a production issue under time pressure?", "difficulty": "Hard"},
            {"category": "Behavioral", "question": "Tell me about a time you had to work with a difficult team member. How did you handle it?", "difficulty": "Medium"},
            {"category": "Behavioral", "question": "How do you prioritize tasks when you have multiple deadlines?", "difficulty": "Easy"},
            {"category": "System Design", "question": f"Design a scalable system for a high-traffic {job_title} application.", "difficulty": "Hard"},
        ]

    async def _call_ai(self, prompt: str) -> str:
        """Call the free AI model (Pollinations or fallback)."""
        import aiohttp
        import urllib.parse

        encoded = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded}"

        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
        except Exception as e:
            logger.warning("pollinations_ai_failed", error=str(e))

        # Second fallback: return empty to trigger regex fallback
        return "{}"

import asyncio
import json
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import async_session_factory
from app.models.candidate import Candidate
from app.models.organization import Organization
from sqlalchemy import select

async def seed_candidates():
    async with async_session_factory() as session:
        # Get first organization
        result = await session.execute(select(Organization))
        org = result.scalars().first()
        if not org:
            print("No organization found. Please create an account first.")
            return

        mock_candidates = [
            {
                "full_name": "Alice Developer",
                "email": "alice@example.com",
                "phone": "+1-555-0101",
                "resume_text": "Experienced Python developer with 5 years of experience in Django and FastAPI.",
                "resume_filename": "alice_resume.pdf",
                "current_role": "Backend Engineer",
                "years_of_experience": 5.0,
                "skills": ["Python", "FastAPI", "Django", "PostgreSQL"],
                "experience": [{"role": "Backend Engineer", "company": "Tech Corp", "duration": "3 years"}],
                "education": [{"degree": "B.S. Computer Science", "institution": "State University", "year": "2019"}],
                "job_title": "Senior Backend Developer",
                "overall_score": 92.0,
                "stage": "new"
            },
            {
                "full_name": "Bob Manager",
                "email": "bob@example.com",
                "phone": "+1-555-0202",
                "resume_text": "Product manager with a track record of delivering successful SaaS products.",
                "resume_filename": "bob_pm_resume.pdf",
                "current_role": "Product Manager",
                "years_of_experience": 7.0,
                "skills": ["Product Strategy", "Agile", "Scrum", "Jira"],
                "experience": [{"role": "Product Manager", "company": "Innovate Inc", "duration": "4 years"}],
                "education": [{"degree": "MBA", "institution": "Business School", "year": "2016"}],
                "job_title": "Product Lead",
                "overall_score": 85.0,
                "stage": "shortlisted"
            },
            {
                "full_name": "Charlie Designer",
                "email": "charlie@example.com",
                "phone": "+1-555-0303",
                "resume_text": "UX/UI designer creating beautiful and accessible interfaces.",
                "resume_filename": "charlie_ux.pdf",
                "current_role": "UX/UI Designer",
                "years_of_experience": 3.0,
                "skills": ["Figma", "UI/UX", "CSS", "Wireframing"],
                "experience": [{"role": "UI Designer", "company": "Design Studio", "duration": "3 years"}],
                "education": [{"degree": "B.A. Graphic Design", "institution": "Art Institute", "year": "2021"}],
                "job_title": "Product Designer",
                "overall_score": 78.0,
                "stage": "interview_scheduled"
            }
        ]

        for c_data in mock_candidates:
            # Check if candidate already exists
            existing = await session.execute(
                select(Candidate).where(Candidate.email == c_data["email"], Candidate.organization_id == org.id)
            )
            if existing.scalar_one_or_none():
                print(f"Candidate {c_data['full_name']} already exists.")
                continue

            candidate = Candidate(
                organization_id=org.id,
                full_name=c_data["full_name"],
                email=c_data["email"],
                phone=c_data["phone"],
                resume_text=c_data["resume_text"],
                resume_filename=c_data["resume_filename"],
                current_role=c_data["current_role"],
                years_of_experience=c_data["years_of_experience"],
                skills_json=json.dumps(c_data["skills"]),
                experience_json=json.dumps(c_data["experience"]),
                education_json=json.dumps(c_data["education"]),
                job_title=c_data["job_title"],
                overall_score=c_data["overall_score"],
                stage=c_data["stage"]
            )
            session.add(candidate)
        
        await session.commit()
        print("Mock candidates seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_candidates())

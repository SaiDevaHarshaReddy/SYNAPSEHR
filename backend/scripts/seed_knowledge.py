"""Seed knowledge base with default HR policy documents."""

import asyncio
import os
import uuid
from datetime import datetime, timezone

from app.database.database import async_session_factory, init_db
from app.models.policy_document import PolicyDocument
from app.models.organization import Organization
from app.core.config import get_settings

settings = get_settings()

# Default HR policy documents
POLICY_DOCUMENTS = [
    {
        "title": "Employee Leave Policy",
        "category": "leave",
        "content": """# Employee Leave Policy

## Overview
SynapseHR provides comprehensive leave benefits to support work-life balance for all employees.

## Types of Leave

### 1. Casual Leave
- Employees are entitled to 12 casual leaves per year
- Casual leaves can be taken in units of half-day or full-day
- Prior approval from reporting manager is required
- Casual leaves cannot be carried forward to the next year

### 2. Sick Leave
- Employees are entitled to 10 sick leaves per year
- Medical certificate may be required for leaves exceeding 3 consecutive days
- Sick leaves can be carried forward up to 5 days to the next year

### 3. Annual Leave (Earned Leave)
- Employees are entitled to 15 annual leaves per year
- Annual leaves must be applied at least 7 days in advance
- Maximum 5 annual leaves can be carried forward
- encashment of up to 5 unused annual leaves is allowed

### 4. Maternity Leave
- Female employees are entitled to 26 weeks of maternity leave
- Maternity leave is applicable for up to 2 surviving children
- Full salary is paid during maternity leave

### 5. Paternity Leave
- Male employees are entitled to 10 days of paternity leave
- Paternity leave must be availed within 15 days from the date of delivery

## Leave Application Process
1. Apply through the HR portal or AI assistant
2. Select leave type, dates, and provide reason
3. Approval from reporting manager
4. Leave balance will be updated automatically

## Important Notes
- Leave balance is credited on January 1st of each year
- Leaves cannot be applied retroactively for more than 7 days
- Abandonment of employment without notice forfeits leave encashment
""",
    },
    {
        "title": "Work From Home Policy",
        "category": "remote_work",
        "content": """# Work From Home (WFH) Policy

## Eligibility
- All full-time employees are eligible for remote work arrangements
- Manager approval is required for regular WFH arrangements
- Hybrid work model: minimum 3 days in office per week

## Guidelines

### Equipment and Setup
- Company will provide laptop and necessary software licenses
- Employees must ensure stable internet connectivity (minimum 50 Mbps recommended)
- Use of VPN is mandatory for accessing company resources
- Dedicated workspace with ergonomic setup is recommended

### Working Hours
- Core working hours: 10:00 AM to 4:00 PM (local time)
- Flexible hours outside core hours with manager agreement
- Must be available on Slack/Teams during core hours

### Communication
- Daily standup meetings are mandatory (virtual or in-person)
- Weekly team sync meetings
- Monthly one-on-one with reporting manager
- Keep calendar updated with availability

### Security
- Never share login credentials or VPN access
- Lock screen when stepping away from workstation
- Use only approved cloud storage for work files
- Report security incidents immediately

## Approval Process
1. Discuss with reporting manager
2. Submit WFH request through HR portal
3. Manager approves/rejects within 2 business days
4. Approved arrangement is reviewed quarterly
""",
    },
    {
        "title": "Code of Conduct",
        "category": "compliance",
        "content": """# Code of Conduct

## Our Values
At SynapseHR, we uphold the highest standards of integrity and professionalism.

## Professional Behavior
- Treat all colleagues, clients, and partners with respect and dignity
- Maintain a inclusive and discrimination-free workplace
- Communicate honestly and transparently
- Take responsibility for your actions and decisions

## Anti-Discrimination and Harassment
- Zero tolerance for discrimination based on race, gender, religion, age, disability, or any protected characteristic
- Sexual harassment in any form is strictly prohibited
- All complaints will be investigated promptly and confidentially
- Retaliation against complainants is prohibited

## Conflicts of Interest
- Disclose any potential conflicts of interest to your manager
- Avoid situations where personal interests conflict with company interests
- Do not use company resources for personal gain
- Report any perceived conflicts immediately

## Data Protection and Confidentiality
- Protect customer and employee data at all times
- Follow data handling procedures as per company policy
- Never share confidential information with unauthorized parties
- Report data breaches immediately to the IT security team

## Social Media and Public Communications
- Do not share company confidential information on social media
- Represent the company professionally in public forums
- Clearly state personal views are your own when discussing work-related topics
- Seek approval before making public statements on behalf of the company

## Reporting Violations
- Report any violations to your manager, HR, or through the anonymous ethics hotline
- All reports will be treated confidentially
- Investigations will be conducted fairly and promptly
""",
    },
    {
        "title": "Compensation and Benefits",
        "category": "compensation",
        "content": """# Compensation and Benefits

## Salary Structure
- Competitive salary benchmarked against industry standards
- Annual performance-based increments (April cycle)
- Salary revision upon promotion or role change

## Benefits Package

### Health Insurance
- Comprehensive health insurance for employee + family (spouse + 2 children)
- Coverage includes hospitalization, day care procedures, and maternity
- Network hospitals across 50+ cities
- Sum insured: $50,000 per annum

### Dental and Vision
- Annual dental checkup covered
- Vision correction allowance up to $500 per year

### Retirement Benefits
- 401(k) matching: Company matches up to 6% of salary
- Vesting period: 3 years (20% per year)

### Stock Options
- ESOP available for employees with 1+ year tenure
- Vested over 4 years with 1-year cliff

### Other Benefits
- Flexible spending account (FSA)
- Commuter benefits
- Employee assistance program (EAP)
- Gym membership reimbursement up to $100/month
- Learning and development budget: $2,000/year

## Leave Encashment
- Unused annual leaves can be encashed at the time of separation
- Encashment rate: Basic salary / 30 days per leave

## Pay Schedule
- Monthly salary credited on the last working day of the month
- Direct deposit to designated bank account
""",
    },
    {
        "title": "Performance Management",
        "category": "performance",
        "content": """# Performance Management

## Review Cycle
- Annual performance review: January - December
- Mid-year review: July
- Quarterly check-ins with manager

## Performance Levels
1. **Exceptional** (5): Consistently exceeds all expectations
2. **Exceeds Expectations** (4): Regularly exceeds expectations
3. **Meets Expectations** (3): Consistently meets expectations
4. **Needs Improvement** (2): Sometimes fails to meet expectations
5. **Unsatisfactory** (1): Consistently fails to meet expectations

## Goal Setting
- SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)
- Goals aligned with team and company objectives
- Minimum 3 goals, maximum 5 goals per review cycle
- Goals documented in HR portal by January 31st

## Review Process
1. Self-assessment submission (January)
2. Manager assessment (February)
3. Calibration sessions (March)
4. Review discussion with employee (March)
5. Final rating and compensation decisions (April)

## Improvement Plans
- Performance Improvement Plan (PIP) for ratings below 3
- Duration: 30-90 days
- Weekly check-ins with manager
- Clear milestones and expectations
- Support and resources provided

## Career Development
- Individual Development Plans (IDPs) discussed during reviews
- Training and certification sponsorship
- Internal mobility and promotion opportunities
- Mentorship program available
""",
    },
    {
        "title": "Onboarding Process",
        "category": "onboarding",
        "content": """# Employee Onboarding Process

## Before First Day (Pre-boarding)
- Welcome email with first-day instructions
- Equipment setup (laptop, access cards, etc.)
- IT account creation (email, Slack, HR portal)
- Buddy assignment

## Day 1: Welcome and Orientation
- Welcome meeting with HR
- Company overview and culture introduction
- Office tour and introductions
- Equipment handover and setup verification
- Complete paperwork (employment contract, tax forms, etc.)

## Week 1: Foundation
- Role-specific training schedule
- Meet key stakeholders and team members
- Access to required tools and systems
- Review of company policies and procedures
- First meeting with reporting manager

## Month 1: Integration
- Daily check-ins with buddy
- Complete mandatory training modules
- First project assignment
- 30-day review with manager
- Feedback collection

## Month 3: Establishment
- 90-day review with manager
- Goal setting for first year
- Full integration into team processes
- Performance expectations clarification

## Onboarding Checklist
- [ ] Welcome kit received
- [ ] IT accounts activated
- [ ] Employment contract signed
- [ ] Benefits enrollment completed
- [ ] Mandatory training completed
- [ ] Team introductions done
- [ ] First project assigned
- [ ] 30-day review completed
- [ ] 90-day review completed

## Key Contacts During Onboarding
- HR Point of Contact: [Assigned HR]
- IT Support: itsupport@synapsehr.com
- Buddy: [Assigned Buddy]
- Manager: [Reporting Manager]
""",
    },
]


async def seed_knowledge_base():
    """Seed the knowledge base with default policy documents."""
    await init_db()

    knowledge_dir = settings.KNOWLEDGE_DIR
    os.makedirs(knowledge_dir, exist_ok=True)

    async with async_session_factory() as session:
        from sqlalchemy import select

        # Get the first organization
        org_result = await session.execute(select(Organization))
        org = org_result.scalar_one_or_none()
        if not org:
            print("No organization found. Please run the main seed script first.")
            return

        org_id = org.id

        # Check if documents already exist for this org
        result = await session.execute(
            select(PolicyDocument).where(PolicyDocument.organization_id == org_id)
        )
        existing_docs = result.scalars().all()

        if existing_docs:
            print(f"Knowledge base already has {len(existing_docs)} documents for this organization. Skipping seed.")
            return

        print("Seeding knowledge base with default HR policy documents...")

        # Create policy documents and text files
        for doc_data in POLICY_DOCUMENTS:
            doc_id = uuid.uuid4()
            file_name = f"{doc_id}.txt"
            file_path = os.path.join(knowledge_dir, file_name)

            # Write content to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(doc_data["content"])

            # Create database record
            policy_doc = PolicyDocument(
                id=doc_id,
                organization_id=org_id,
                title=doc_data["title"],
                category=doc_data["category"],
                file_name=file_name,
                storage_path=file_path,
                version=1,
                uploaded_by=None,
            )
            session.add(policy_doc)
            print(f"  Created: {doc_data['title']} ({doc_data['category']})")

        await session.commit()

        # Index into vector store
        print("\nIndexing documents into vector store...")
        try:
            from app.rag.retriever import Retriever

            retriever = Retriever()

            for doc_data in POLICY_DOCUMENTS:
                result = await session.execute(
                    select(PolicyDocument).where(
                        PolicyDocument.organization_id == org_id,
                        PolicyDocument.title == doc_data["title"]
                    )
                )
                doc = result.scalar_one_or_none()
                if doc:
                    chunk_count = await retriever.index_document(
                        file_path=doc.storage_path,
                        document_id=str(doc.id),
                        organization_id=str(org_id),
                        title=doc_data["title"],
                        category=doc_data["category"],
                    )
                    print(f"  Indexed: {doc_data['title']} ({chunk_count} chunks)")

            print("\nKnowledge base seeding complete!")
        except Exception as e:
            print(f"\nWarning: Vector store indexing failed: {e}")
            print("Documents are saved in the database but not indexed for search.")
            print("You can re-index later by re-running this script after setting up ChromaDB.")


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())

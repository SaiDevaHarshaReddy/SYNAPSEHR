"""Seed database with initial data."""

import asyncio
import uuid
from datetime import datetime, timezone, date

from app.core.security import hash_password
from app.database.database import async_session_factory, init_db
from app.models.department import Department
from app.models.employee import Employee
from app.models.leave_balance import LeaveBalance
from app.models.leave_type import LeaveType
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.leave_request import LeaveRequest
import app.models.candidate  # noqa
from app.models.candidate import Candidate


async def seed_database():
    """Seed the database with initial data."""
    await init_db()

    async with async_session_factory() as session:
        # ── Organization ──────────────────────────────────────────────────
        org = Organization(
            id=uuid.uuid4(),
            name="SynapseHR Demo",
            email="admin@synapsehr.com",
            phone="+1-555-0100",
            address="123 Business St, Tech City, TC 12345",
        )
        session.add(org)

        # ── Roles ─────────────────────────────────────────────────────────
        roles = {}
        for role_name, description in [
            ("employee", "Basic employee access"),
            ("manager", "Team management access"),
            ("hr", "Human resources access"),
            ("administrator", "Full system access"),
        ]:
            role = Role(id=uuid.uuid4(), name=role_name, description=description)
            session.add(role)
            roles[role_name] = role

        # ── Admin user (no employee profile — system admin) ───────────────
        admin_user = User(
            id=uuid.uuid4(),
            organization_id=org.id,
            role_id=roles["administrator"].id,
            email="admin@synapsehr.com",
            password_hash=hash_password("Admin@123"),
            is_active=True,
        )
        session.add(admin_user)

        # ── Departments ───────────────────────────────────────────────────
        departments = {}
        for dept_name, description in [
            ("Engineering", "Software development and technical operations"),
            ("Human Resources", "People management and organizational development"),
            ("Marketing", "Brand management and customer acquisition"),
            ("Finance", "Financial planning and accounting"),
            ("Operations", "Business operations and support"),
        ]:
            dept = Department(
                id=uuid.uuid4(),
                organization_id=org.id,
                name=dept_name,
                description=description,
            )
            session.add(dept)
            departments[dept_name] = dept

        # ── HR Manager – Sarah Johnson ────────────────────────────────────
        hr_user = User(
            id=uuid.uuid4(), organization_id=org.id,
            role_id=roles["hr"].id,
            email="hr@synapsehr.com",
            password_hash=hash_password("HR@12345"), is_active=True,
        )
        session.add(hr_user)
        hr_emp = Employee(
            id=uuid.uuid4(), user_id=hr_user.id,
            department_id=departments["Human Resources"].id,
            employee_code="EMP001", first_name="Sarah", last_name="Johnson",
            designation="HR Manager", phone="+1-555-0101",
            joining_date=date(2023, 1, 15), employment_type="full_time", status="active",
        )
        session.add(hr_emp)

        # ── Engineering Manager – Michael Chen ────────────────────────────
        mgr_user = User(
            id=uuid.uuid4(), organization_id=org.id,
            role_id=roles["manager"].id,
            email="manager@synapsehr.com",
            password_hash=hash_password("Manager@123"), is_active=True,
        )
        session.add(mgr_user)
        mgr_emp = Employee(
            id=uuid.uuid4(), user_id=mgr_user.id,
            department_id=departments["Engineering"].id,
            employee_code="EMP002", first_name="Michael", last_name="Chen",
            designation="Engineering Manager", phone="+1-555-0102",
            joining_date=date(2022, 6, 1), employment_type="full_time", status="active",
        )
        session.add(mgr_emp)

        # ── Employee – Alex Williams ──────────────────────────────────────
        emp_user = User(
            id=uuid.uuid4(), organization_id=org.id,
            role_id=roles["employee"].id,
            email="employee@synapsehr.com",
            password_hash=hash_password("Employee@123"), is_active=True,
        )
        session.add(emp_user)
        alex_emp = Employee(
            id=uuid.uuid4(), user_id=emp_user.id,
            department_id=departments["Engineering"].id,
            employee_code="EMP003", first_name="Alex", last_name="Williams",
            designation="Software Engineer", phone="+1-555-0103",
            manager_id=mgr_emp.id,
            joining_date=date(2024, 3, 15), employment_type="full_time", status="active",
        )
        session.add(alex_emp)

        # ── Additional employees (15 more across all departments) ─────────
        extra_data = [
            # Engineering
            ("Jessica",   "Taylor",   "EMP004", "Engineering",     "Frontend Developer",     "jessica@synapsehr.com",   "+1-555-0104", "employee", "jessica123"),
            ("David",     "Kim",      "EMP005", "Engineering",     "Backend Engineer",       "david@synapsehr.com",     "+1-555-0105", "employee", "david123"),
            ("Ravi",      "Patel",    "EMP006", "Engineering",     "DevOps Engineer",        "ravi@synapsehr.com",      "+1-555-0106", "employee", "ravi123"),
            ("Zara",      "Ahmed",    "EMP007", "Engineering",     "QA Engineer",            "zara@synapsehr.com",      "+1-555-0107", "employee", "zara123"),
            # Human Resources
            ("Priscilla", "Moore",    "EMP008", "Human Resources", "HR Business Partner",    "priscilla@synapsehr.com", "+1-555-0108", "employee", "priscilla123"),
            ("Thomas",    "Brown",    "EMP009", "Human Resources", "Talent Acquisition Lead","thomas@synapsehr.com",    "+1-555-0109", "employee", "thomas123"),
            # Marketing
            ("Emily",     "Davis",    "EMP010", "Marketing",       "Marketing Manager",      "emily@synapsehr.com",     "+1-555-0110", "manager",  "emily123"),
            ("James",     "Wilson",   "EMP011", "Marketing",       "Content Strategist",     "james@synapsehr.com",     "+1-555-0111", "employee", "james123"),
            ("Sophia",    "Li",       "EMP012", "Marketing",       "Digital Marketing Spec", "sophia@synapsehr.com",    "+1-555-0112", "employee", "sophia123"),
            # Finance
            ("Robert",    "Martinez", "EMP013", "Finance",         "Finance Manager",        "robert@synapsehr.com",    "+1-555-0113", "manager",  "robert123"),
            ("Linda",     "Anderson", "EMP014", "Finance",         "Senior Accountant",      "linda@synapsehr.com",     "+1-555-0114", "employee", "linda123"),
            ("Kevin",     "Thompson", "EMP015", "Finance",         "Financial Analyst",      "kevin@synapsehr.com",     "+1-555-0115", "employee", "kevin123"),
            # Operations
            ("Nina",      "Garcia",   "EMP016", "Operations",      "Operations Manager",     "nina@synapsehr.com",      "+1-555-0116", "manager",  "nina123"),
            ("Chris",     "Lee",      "EMP017", "Operations",      "Supply Chain Lead",      "chris@synapsehr.com",     "+1-555-0117", "employee", "chris123"),
            ("Anita",     "Kumar",    "EMP018", "Operations",      "Process Analyst",        "anita@synapsehr.com",     "+1-555-0118", "employee", "anita123"),
        ]

        all_employees = [hr_emp, mgr_emp, alex_emp]
        joining_dates = [
            date(2023, 3, 10), date(2023, 7, 20), date(2023, 11, 5),
            date(2024, 1, 8),  date(2022, 9, 14), date(2023, 4, 22),
            date(2021, 8, 1),  date(2024, 2, 19), date(2023, 6, 30),
            date(2020, 5, 1),  date(2022, 10, 3), date(2024, 4, 11),
            date(2021, 3, 22), date(2023, 9, 17), date(2024, 5, 1),
        ]

        for i, (first, last, code, dept_name, design, email, phone, role_name, pwd) in enumerate(extra_data):
            u = User(
                id=uuid.uuid4(), organization_id=org.id,
                role_id=roles[role_name].id,
                email=email,
                password_hash=hash_password(pwd), is_active=True,
            )
            session.add(u)
            e = Employee(
                id=uuid.uuid4(), user_id=u.id,
                department_id=departments[dept_name].id,
                employee_code=code, first_name=first, last_name=last,
                designation=design, phone=phone,
                manager_id=mgr_emp.id if dept_name == "Engineering" else None,
                joining_date=joining_dates[i],
                employment_type="full_time",
                status="active",
            )
            session.add(e)
            all_employees.append(e)

        # ── Leave Types ───────────────────────────────────────────────────
        leave_types = {}
        for name, days, requires_approval, is_paid in [
            ("Casual Leave",    12, True,  True),
            ("Sick Leave",      10, True,  True),
            ("Annual Leave",    15, True,  True),
            ("Maternity Leave", 90, True,  True),
            ("Paternity Leave", 10, True,  True),
            ("Unpaid Leave",     0, True,  False),
        ]:
            lt = LeaveType(
                id=uuid.uuid4(),
                organization_id=org.id,
                name=name,
                days_per_year=days,
                requires_approval=requires_approval,
                is_paid=is_paid,
            )
            session.add(lt)
            leave_types[name] = lt

        # ── Leave Balances for every employee ─────────────────────────────
        for emp in all_employees:
            for lt in leave_types.values():
                session.add(LeaveBalance(
                    id=uuid.uuid4(),
                    employee_id=emp.id,
                    leave_type_id=lt.id,
                    available_days=lt.days_per_year,
                    used_days=0,
                    carry_forward_days=0,
                    year=datetime.now().year,
                ))

        # ── Sample Leave Requests (rich set for analytics) ────────────────
        sample_requests = [
            (alex_emp,   "Casual Leave",    date(2026, 7, 10), date(2026, 7, 15), "pending",  "Family summer vacation"),
            (alex_emp,   "Sick Leave",      date(2026, 7, 5),  date(2026, 7, 5),  "approved", "Dental procedure"),
            (hr_emp,     "Casual Leave",    date(2026, 6, 12), date(2026, 6, 14), "approved", "Long weekend"),
            (mgr_emp,    "Annual Leave",    date(2026, 6, 20), date(2026, 6, 25), "rejected", "Project crunch"),
            (alex_emp,   "Annual Leave",    date(2026, 5, 1),  date(2026, 5, 5),  "cancelled","Deferred"),
            (all_employees[3], "Sick Leave",   date(2026, 7, 1), date(2026, 7, 2),  "approved", "Flu"),
            (all_employees[4], "Casual Leave", date(2026, 7, 8), date(2026, 7, 8),  "pending",  "Personal"),
            (all_employees[5], "Annual Leave", date(2026, 6, 1), date(2026, 6, 10), "approved", "Vacation"),
            (all_employees[6], "Casual Leave", date(2026, 7, 12),date(2026, 7, 14), "pending",  "Wedding"),
            (all_employees[7], "Sick Leave",   date(2026, 6, 28),date(2026, 6, 29), "approved", "Doctor visit"),
            (all_employees[8], "Annual Leave", date(2026, 5, 15),date(2026, 5, 25), "approved", "Summer holiday"),
            (all_employees[9], "Casual Leave", date(2026, 7, 20),date(2026, 7, 21), "pending",  "Travel"),
        ]

        for emp, lt_name, start, end, status, reason in sample_requests:
            session.add(LeaveRequest(
                id=uuid.uuid4(),
                employee_id=emp.id,
                leave_type_id=leave_types[lt_name].id,
                start_date=start,
                end_date=end,
                status=status,
                reason=reason,
            ))

        # ── Candidates for Recruitment ────────────────────────────────────
        import json
        candidates_data = [
            {
                "full_name": "Priya Sharma",      "email": "priya.sharma@example.com",  "phone": "+91-9876543210",
                "current_role": "Senior Python Developer", "years_of_experience": 5.0,
                "skills": ["Python", "FastAPI", "Django", "PostgreSQL", "Docker", "AWS"],
                "education": [{"degree": "B.Tech CS", "institution": "IIT Delhi", "year": "2019"}],
                "experience": [{"role": "Senior Python Developer", "company": "TechCorp", "duration": "3 years", "description": "Built microservices"}],
                "job_title": "Python Backend Engineer",
                "overall_score": 88.5, "skill_match_score": 92.0, "experience_score": 85.0,
                "education_score": 80.0, "recommendation": "Highly Recommended", "stage": "shortlisted",
            },
            {
                "full_name": "Rahul Verma",        "email": "rahul.verma@example.com",   "phone": "+91-9123456780",
                "current_role": "Frontend Engineer", "years_of_experience": 3.0,
                "skills": ["React", "TypeScript", "Vue", "CSS", "Tailwind", "JavaScript"],
                "education": [{"degree": "B.Sc CS", "institution": "VIT", "year": "2021"}],
                "experience": [{"role": "Frontend Developer", "company": "Infosys", "duration": "3 years", "description": "Built responsive UIs"}],
                "job_title": "React Developer",
                "overall_score": 75.0, "skill_match_score": 80.0, "experience_score": 70.0,
                "education_score": 72.0, "recommendation": "Recommended", "stage": "interview_scheduled",
            },
            {
                "full_name": "Ananya Patel",       "email": "ananya.patel@example.com",  "phone": "+91-9988776655",
                "current_role": "Data Scientist", "years_of_experience": 4.0,
                "skills": ["Python", "Machine Learning", "TensorFlow", "Pandas", "SQL", "Tableau"],
                "education": [{"degree": "M.Sc Data Science", "institution": "BITS Pilani", "year": "2020"}],
                "experience": [{"role": "Data Scientist", "company": "Analytics Co", "duration": "4 years", "description": "Built ML models"}],
                "job_title": "Machine Learning Engineer",
                "overall_score": 82.0, "skill_match_score": 85.0, "experience_score": 80.0,
                "education_score": 90.0, "recommendation": "Highly Recommended", "stage": "shortlisted",
            },
            {
                "full_name": "Karan Mehta",        "email": "karan.mehta@example.com",   "phone": "+91-9700000111",
                "current_role": "DevOps Engineer", "years_of_experience": 2.5,
                "skills": ["Docker", "Kubernetes", "Jenkins", "AWS", "Terraform", "Linux"],
                "education": [{"degree": "B.E IT", "institution": "Pune University", "year": "2022"}],
                "experience": [{"role": "DevOps Engineer", "company": "CloudOps", "duration": "2.5 years", "description": "CI/CD pipelines"}],
                "job_title": "DevOps Engineer",
                "overall_score": 68.0, "skill_match_score": 72.0, "experience_score": 65.0,
                "education_score": 70.0, "recommendation": "Consider", "stage": "new",
            },
            {
                "full_name": "Sneha Reddy",        "email": "sneha.reddy@example.com",   "phone": "+91-9555001122",
                "current_role": "HR Manager", "years_of_experience": 6.0,
                "skills": ["Recruitment", "HRMS", "Payroll", "Employee Relations", "Onboarding"],
                "education": [{"degree": "MBA HR", "institution": "XLRI", "year": "2018"}],
                "experience": [{"role": "HR Manager", "company": "Fortune 500", "duration": "6 years", "description": "Led HR operations"}],
                "job_title": "HR Business Partner",
                "overall_score": 91.0, "skill_match_score": 90.0, "experience_score": 92.0,
                "education_score": 95.0, "recommendation": "Highly Recommended", "stage": "offer_sent",
            },
            {
                "full_name": "Arjun Nair",         "email": "arjun.nair@example.com",    "phone": "+91-9871234560",
                "current_role": "Full Stack Developer", "years_of_experience": 4.0,
                "skills": ["React", "Node.js", "Express", "MongoDB", "TypeScript", "AWS"],
                "education": [{"degree": "B.Tech IT", "institution": "NIT Calicut", "year": "2020"}],
                "experience": [{"role": "Full Stack Developer", "company": "StartupX", "duration": "4 years", "description": "Built SaaS products"}],
                "job_title": "Full Stack Engineer",
                "overall_score": 79.0, "skill_match_score": 84.0, "experience_score": 77.0,
                "education_score": 75.0, "recommendation": "Recommended", "stage": "new",
            },
            {
                "full_name": "Meera Krishnan",     "email": "meera.k@example.com",       "phone": "+91-9900112233",
                "current_role": "Product Manager", "years_of_experience": 7.0,
                "skills": ["Product Strategy", "Agile", "Jira", "Figma", "SQL", "Analytics"],
                "education": [{"degree": "MBA", "institution": "IIM Bangalore", "year": "2017"}],
                "experience": [{"role": "Product Manager", "company": "MegaTech", "duration": "7 years", "description": "Led product roadmap"}],
                "job_title": "Senior Product Manager",
                "overall_score": 93.0, "skill_match_score": 88.0, "experience_score": 95.0,
                "education_score": 98.0, "recommendation": "Highly Recommended", "stage": "hired",
            },
        ]

        for cd in candidates_data:
            session.add(Candidate(
                id=uuid.uuid4(),
                organization_id=org.id,
                full_name=cd["full_name"],
                email=cd["email"],
                phone=cd["phone"],
                current_role=cd["current_role"],
                years_of_experience=cd["years_of_experience"],
                skills_json=json.dumps(cd["skills"]),
                education_json=json.dumps(cd["education"]),
                experience_json=json.dumps(cd["experience"]),
                certifications_json=json.dumps([]),
                languages_json=json.dumps(["English"]),
                projects_json=json.dumps([]),
                job_title=cd["job_title"],
                overall_score=cd["overall_score"],
                skill_match_score=cd["skill_match_score"],
                experience_score=cd["experience_score"],
                education_score=cd["education_score"],
                recommendation=cd["recommendation"],
                missing_skills_json=json.dumps([]),
                stage=cd["stage"],
                resume_filename="sample_resume.pdf",
            ))

        await session.commit()
        total_emp = len(all_employees)
        print(f"✅ Database seeded – {total_emp} employees, 6 leave types, {len(candidates_data)} candidates!")
        print("\nDemo Accounts:")
        print("  Admin:    admin@synapsehr.com / Admin@123")
        print("  HR:       hr@synapsehr.com / HR@12345")
        print("  Manager:  manager@synapsehr.com / Manager@123")
        print("  Employee: employee@synapsehr.com / Employee@123")

    # Seed knowledge base
    print("\n--- Seeding Knowledge Base ---")
    try:
        from scripts.seed_knowledge import seed_knowledge_base
        await seed_knowledge_base()
    except Exception as e:
        print(f"Knowledge base seeding skipped: {e}")


if __name__ == "__main__":
    asyncio.run(seed_database())

import asyncio
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)

async def test():
    from app.models.leave_request import LeaveRequest
    from app.models.employee import Employee
    from app.models.user import User

    async with async_session() as session:
        # Get an org ID
        result = await session.execute(select(User.organization_id).limit(1))
        org_id = result.scalar()
        print("Using org ID:", org_id)

        try:
            result = await session.execute(
                select(LeaveRequest)
                .options(joinedload(LeaveRequest.employee), joinedload(LeaveRequest.leave_type))
                .join(Employee, LeaveRequest.employee_id == Employee.id)
                .join(User, Employee.user_id == User.id)
                .where(User.organization_id == org_id)
                .order_by(LeaveRequest.created_at.desc())
            )
            reqs = list(result.scalars().all())
            print(f"Found {len(reqs)} requests")
            for req in reqs:
                print(req.id, req.employee.first_name, req.leave_type.name)
        except Exception as e:
            print("Query failed:", e)

if __name__ == "__main__":
    asyncio.run(test())

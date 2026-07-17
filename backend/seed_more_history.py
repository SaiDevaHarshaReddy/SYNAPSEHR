import asyncio
import uuid
import random
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)

async def seed_more_history():
    from app.models.leave_type import LeaveType
    from app.models.employee import Employee
    from app.models.leave_request import LeaveRequest
    from app.models.leave_balance import LeaveBalance

    async with async_session() as session:
        # Get leave types
        result = await session.execute(select(LeaveType))
        leave_types = {lt.name: lt.id for lt in result.scalars().all()}
        
        # Get all employees
        result = await session.execute(select(Employee))
        employees = result.scalars().all()
        
        if not employees or not leave_types:
            print("No employees or leave types found.")
            return

        reasons = {
            'Casual Leave': ['Family emergency', 'Personal work', 'Attending a wedding', 'Moving house'],
            'Sick Leave': ['Fever and cold', 'Medical appointment', 'Dental surgery', 'Not feeling well'],
            'Annual Leave': ['Family vacation', 'Traveling abroad', 'Rest and recuperation'],
            'Maternity Leave': ['Maternity leave'],
            'Paternity Leave': ['Paternity leave']
        }
        
        statuses = ['approved', 'pending', 'rejected', 'cancelled']
        
        # Insert 15 random leave requests across different employees
        for _ in range(15):
            emp = random.choice(employees)
            lt_name = random.choice(list(reasons.keys()))
            lt_id = leave_types.get(lt_name)
            if not lt_id: continue
            
            status = random.choice(statuses)
            reason = random.choice(reasons[lt_name])
            
            start_delta = random.randint(-30, 30)
            duration = random.randint(1, 5)
            
            start_dt = date.today() + timedelta(days=start_delta)
            end_dt = start_dt + timedelta(days=duration)
            
            req = LeaveRequest(
                employee_id=emp.id,
                leave_type_id=lt_id,
                start_date=start_dt,
                end_date=end_dt,
                reason=reason,
                status=status,
                is_read=random.choice([True, False])
            )
            session.add(req)
            
            # If approved, update used_days if it's in the current year
            if status == 'approved' and start_dt.year == 2026:
                result = await session.execute(
                    select(LeaveBalance).where(
                        LeaveBalance.employee_id == emp.id,
                        LeaveBalance.leave_type_id == lt_id,
                        LeaveBalance.year == 2026
                    )
                )
                bal = result.scalars().first()
                if bal:
                    bal.used_days += duration
                    bal.available_days = max(0, bal.available_days - duration)
                    
        await session.commit()
        print("More leave history seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_more_history())

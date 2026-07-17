import asyncio
import uuid
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)

async def seed_data():
    from app.models.leave_type import LeaveType
    from app.models.employee import Employee
    from app.models.leave_balance import LeaveBalance
    from app.models.leave_request import LeaveRequest

    async with async_session() as session:
        # Get leave types
        result = await session.execute(select(LeaveType))
        leave_types = {lt.name: {'id': lt.id, 'days': lt.days_per_year} for lt in result.scalars().all()}
        
        target_types = ['Casual Leave', 'Sick Leave', 'Annual Leave']
        
        # Get all employees
        result = await session.execute(select(Employee))
        employees = result.scalars().all()
        
        year = 2026
        
        # 1. Insert leave balances for all employees
        for emp in employees:
            for lt_name in target_types:
                if lt_name in leave_types:
                    lt_id = leave_types[lt_name]['id']
                    days = leave_types[lt_name]['days']
                    
                    # Check if balance exists
                    result = await session.execute(
                        select(LeaveBalance).where(
                            LeaveBalance.employee_id == emp.id,
                            LeaveBalance.leave_type_id == lt_id,
                            LeaveBalance.year == year
                        )
                    )
                    if not result.scalars().first():
                        lb = LeaveBalance(
                            employee_id=emp.id,
                            leave_type_id=lt_id,
                            available_days=days,
                            used_days=0,
                            carry_forward_days=0,
                            year=year
                        )
                        session.add(lb)
        
        await session.commit()
        
        # 2. Insert example leave requests for the admin employee
        from app.models.user import User
        result = await session.execute(select(User).where(User.email == 'admin@synapsehr.com'))
        admin_user = result.scalars().first()
        
        if admin_user:
            result = await session.execute(select(Employee).where(Employee.user_id == admin_user.id))
            admin_emp = result.scalars().first()
            
            if admin_emp:
                casual_id = leave_types.get('Casual Leave', {}).get('id')
                sick_id = leave_types.get('Sick Leave', {}).get('id')
                annual_id = leave_types.get('Annual Leave', {}).get('id')
                
                examples = [
                    (casual_id, 'approved', 'Family event', 5, 5),
                    (sick_id, 'rejected', 'Feeling unwell', -2, -1),
                    (annual_id, 'pending', 'Vacation', 10, 15)
                ]
                
                for lt_id, status, reason, start_delta, end_delta in examples:
                    if not lt_id: continue
                    result = await session.execute(
                        select(LeaveRequest).where(
                            LeaveRequest.employee_id == admin_emp.id,
                            LeaveRequest.leave_type_id == lt_id,
                            LeaveRequest.status == status
                        )
                    )
                    if not result.scalars().first():
                        start_dt = date.today() + timedelta(days=start_delta)
                        end_dt = date.today() + timedelta(days=end_delta)
                        req = LeaveRequest(
                            employee_id=admin_emp.id,
                            leave_type_id=lt_id,
                            start_date=start_dt,
                            end_date=end_dt,
                            reason=reason,
                            status=status,
                            is_read=False
                        )
                        session.add(req)
                
                # Update used_days for casual leave
                if casual_id:
                    result = await session.execute(
                        select(LeaveBalance).where(
                            LeaveBalance.employee_id == admin_emp.id,
                            LeaveBalance.leave_type_id == casual_id,
                            LeaveBalance.year == year
                        )
                    )
                    bal = result.scalars().first()
                    if bal:
                        bal.used_days = 5
                        bal.available_days = max(0, bal.available_days - 5)
                
                await session.commit()
        print("Supabase Data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())

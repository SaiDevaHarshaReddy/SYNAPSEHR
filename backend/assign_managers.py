import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)

async def assign_managers():
    from app.models.department import Department
    from app.models.employee import Employee

    dept_manager_map = {
        "Engineering": "Michael Chen",
        "Human Resources": "Sarah Johnson",
        "Marketing": "Emily Davis",
        "Finance": "Robert Martinez",
        "Operations": "Nina Garcia",
    }

    async with async_session() as session:
        # Get departments
        dept_res = await session.execute(select(Department))
        depts = dept_res.scalars().all()
        
        # Get employees
        emp_res = await session.execute(select(Employee))
        emps = emp_res.scalars().all()
        
        for dept in depts:
            manager_name = dept_manager_map.get(dept.name)
            if manager_name:
                first, last = manager_name.split(' ', 1)
                manager = next((e for e in emps if e.first_name == first and e.last_name == last), None)
                if manager:
                    dept.manager_id = manager.id
                    print(f"Assigned {manager_name} to {dept.name}")
                else:
                    print(f"Could not find employee {manager_name}")
                    
        await session.commit()
        print("Managers assigned successfully!")

if __name__ == "__main__":
    asyncio.run(assign_managers())

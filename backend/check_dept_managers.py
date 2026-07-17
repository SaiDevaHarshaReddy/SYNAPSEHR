import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)

async def check():
    from app.models.department import Department
    from app.models.employee import Employee

    async with async_session() as session:
        dept_res = await session.execute(select(Department))
        depts = dept_res.scalars().all()
        
        emp_res = await session.execute(select(Employee))
        emps = emp_res.scalars().all()
        emp_dict = {str(e.id): e.first_name + " " + e.last_name for e in emps}
        
        print("Departments:")
        for d in depts:
            manager_name = emp_dict.get(str(d.manager_id)) if d.manager_id else "None"
            print(f"- {d.name} | Manager: {manager_name} ({d.manager_id})")

if __name__ == "__main__":
    asyncio.run(check())

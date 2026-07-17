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
        print("Departments:")
        for d in depts:
            print(f"- {d.id} | {d.name}")

        emp_res = await session.execute(select(Employee.id, Employee.first_name, Employee.last_name, Employee.department_id))
        emps = emp_res.all()
        print(f"\nEmployees ({len(emps)}):")
        for e in emps:
            dept_name = next((d.name for d in depts if d.id == e.department_id), "None")
            print(f"- {e.first_name} {e.last_name} | Dept: {dept_name}")

if __name__ == "__main__":
    asyncio.run(check())

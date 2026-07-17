import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)

async def test():
    from app.models.user import User
    from app.models.role import Role

    async with async_session() as session:
        result = await session.execute(
            select(User, Role)
            .join(Role, User.role_id == Role.id)
            .where(User.email == 'admin@synapsehr.com')
        )
        row = result.first()
        if row:
            user, role = row
            print(f"Admin email: {user.email}, Role name: '{role.name}'")
        else:
            print("Admin user not found")

if __name__ == "__main__":
    asyncio.run(test())

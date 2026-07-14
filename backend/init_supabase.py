import asyncio
from app.database.database import init_db
from app.models import *

async def main():
    print("Initializing Supabase database...")
    await init_db()
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(main())

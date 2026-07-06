import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_db():
    url = "sqlite+aiosqlite:///./synapsehr.db"
    print(f"Connecting to {url}...")
    try:
        engine = create_async_engine(url)
        async with engine.begin() as conn:
            print("Successfully connected!")
            
            # Check tables
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            print(f"Tables: {tables}")
            
            # Check row counts
            for table in tables:
                count_result = await conn.execute(text(f"SELECT count(*) FROM {table}"))
                count = count_result.scalar()
                print(f"Table '{table}' has {count} rows.")
                
        await engine.dispose()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())

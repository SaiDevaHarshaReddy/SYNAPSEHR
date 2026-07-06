import asyncio, os
os.chdir('backend')
import sys
sys.path.append(os.getcwd())
from app.database.database import async_session_maker
from app.services.analytics import AnalyticsService
async def test():
    async with async_session_maker() as s:
        try:
            a = AnalyticsService(s)
            print(await a.get_dashboard_metrics())
        except Exception as e:
            import traceback
            traceback.print_exc()
asyncio.run(test())

import asyncio
from app.modules.statistics.repository import StatisticsRepository

async def main():
    repo = StatisticsRepository()
    try:
        print('START')
        data = await repo.get_user_statistics()
        print('USERS', type(data), data)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())

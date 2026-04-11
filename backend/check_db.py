import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['aimor_lost_found']
    lost = await db.lost_items.count_documents({})
    found = await db.found_items.count_documents({})
    print(f'Lost items: {lost}')
    print(f'Found items: {found}')
    
    # Show sample items
    print('\nLost items:')
    async for item in db.lost_items.find({}):
        print(f'  - {item.get("title")}: status={item.get("status")}')
    
    print('\nFound items:')
    async for item in db.found_items.find({}):
        print(f'  - {item.get("title")}: status={item.get("status")}')
    
    client.close()

asyncio.run(check())

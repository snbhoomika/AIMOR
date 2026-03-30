from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.core.config import settings


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None


database = Database()


async def connect_to_mongo():
    """Create database connection"""
    database.client = AsyncIOMotorClient(settings.MONGODB_URL)
    database.db = database.client[settings.DATABASE_NAME]

    # Create indexes for better performance
    await create_indexes()
    print(f"Connected to MongoDB: {settings.DATABASE_NAME}")


async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        print("Disconnected from MongoDB")


async def create_indexes():
    """Create necessary indexes for collections"""
    db = database.db

    # Users collection indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("phone", sparse=True)

    # Lost items indexes
    await db.lost_items.create_index("user_id")
    await db.lost_items.create_index("category")
    await db.lost_items.create_index("status")
    await db.lost_items.create_index([("location", "2dsphere")])
    await db.lost_items.create_index("created_at")

    # Found items indexes
    await db.found_items.create_index("user_id")
    await db.found_items.create_index("category")
    await db.found_items.create_index("status")
    await db.found_items.create_index([("location", "2dsphere")])
    await db.found_items.create_index("created_at")

    # Claims indexes
    await db.claims.create_index("lost_item_id")
    await db.claims.create_index("found_item_id")
    await db.claims.create_index("status")

    # Notifications indexes
    await db.notifications.create_index("user_id")
    await db.notifications.create_index("read")
    await db.notifications.create_index("created_at")


def get_database():
    """Get database instance"""
    return database.db

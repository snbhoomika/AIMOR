"""
Database initialization script
Run this script to set up initial database structure and indexes
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import create_indexes


async def init_database():
    """Initialize database with indexes and sample data"""
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    # Create indexes
    print("Creating indexes...")
    await create_indexes(db)
    print("Indexes created successfully!")

    # Check if admin user exists
    admin_exists = await db.users.find_one({"email": "admin@aimor.com"})
    
    if not admin_exists:
        print("Creating admin user...")
        from app.utils.security import get_password_hash
        
        admin_user = {
            "email": "admin@aimor.com",
            "full_name": "Admin User",
            "hashed_password": get_password_hash("admin123"),
            "phone": "+1234567890",
            "role": "admin",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        await db.users.insert_one(admin_user)
        print("Admin user created (email: admin@aimor.com, password: admin123)")
    
    # Close connection
    client.close()
    print("Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_database())

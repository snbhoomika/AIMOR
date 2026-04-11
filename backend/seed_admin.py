import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "aimor_lost_found"

async def seed_admin():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    admin_email = "admin@aimor.com"
    admin_password = "admin123"
    
    existing = await db.users.find_one({"email": admin_email})
    if existing:
        print("Admin user already exists")
    else:
        hashed = pwd_context.hash(admin_password)
        admin = {
            "email": admin_email,
            "full_name": "Admin User",
            "phone": "+1234567890",
            "hashed_password": hashed,
            "role": "admin",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await db.users.insert_one(admin)
        print(f"Admin user created: {admin_email}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_admin())

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "aimor_lost_found"

async def reset_admin():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    admin_email = "admin@aimor.com"
    new_password = "admin123"
    
    hashed = pwd_context.hash(new_password)
    result = await db.users.update_one(
        {"email": admin_email},
        {
            "$set": {
                "hashed_password": hashed,
                "updated_at": datetime.utcnow(),
            }
        }
    )
    
    if result.modified_count > 0 or result.matched_count > 0:
        print(f"Admin password reset for: {admin_email}")
    else:
        print("Admin user not found")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(reset_admin())

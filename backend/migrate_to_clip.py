import asyncio
import base64
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.image_features import get_feature_extractor

async def migrate_images_to_clip():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['aimor_lost_found']
    
    print("Loading CLIP model...")
    extractor = get_feature_extractor()
    
    # Process lost_items
    print("Processing lost_items with CLIP...")
    async for item in db.lost_items.find({}):
        images = item.get("images", [])
        if images and images[0].startswith("data:"):
            try:
                base64_data = images[0].split("base64,")[1]
                image_bytes = base64.b64decode(base64_data)
                
                # Extract CLIP features
                features = extractor.extract_image_features(image_bytes)
                
                await db.lost_items.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"image_embedding": features}}
                )
                print(f"  Updated: {item['title']}")
            except Exception as e:
                print(f"  Error with {item['title']}: {e}")
    
    # Process found_items
    print("Processing found_items with CLIP...")
    async for item in db.found_items.find({}):
        images = item.get("images", [])
        if images and images[0].startswith("data:"):
            try:
                base64_data = images[0].split("base64,")[1]
                image_bytes = base64.b64decode(base64_data)
                
                # Extract CLIP features
                features = extractor.extract_image_features(image_bytes)
                
                await db.found_items.update_one(
                    {"_id": item["_id"]},
                    {"$set": {"image_embedding": features}}
                )
                print(f"  Updated: {item['title']}")
            except Exception as e:
                print(f"  Error with {item['title']}: {e}")
    
    print("Migration to CLIP embeddings complete!")
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_images_to_clip())

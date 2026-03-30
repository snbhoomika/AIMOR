from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import numpy as np

from app.models.item import (
    LostItemResponse,
    FoundItemResponse,
    ItemCategory,
    ItemStatus,
)
from app.utils.security import get_current_user, str_to_object_id
from app.utils.file_handler import save_upload_file
from app.core.database import get_database
from app.core.config import settings

router = APIRouter(prefix="/search", tags=["Search & Matching"])


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if not vec1 or not vec2:
        return 0.0
    
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    
    dot_product = np.dot(vec1_np, vec2_np)
    norm1 = np.linalg.norm(vec1_np)
    norm2 = np.linalg.norm(vec2_np)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


@router.post("/image")
async def search_by_image(
    image: UploadFile = File(...),
    category: Optional[ItemCategory] = None,
    limit: int = Query(10, ge=1, le=50),
    item_type: str = Query("found", regex="^(lost|found|all)$"),
    current_user: dict = Depends(get_current_user),
):
    """
    Search for matching items by uploading an image
    This endpoint simulates ML-based image matching
    """
    db = get_database()
    
    # Upload the search image
    image_url = await save_upload_file(image, subfolder="search")
    
    # TODO: In production, call ML service to extract image embedding
    # For now, we'll simulate with text-based search
    
    # Build query
    collection = "found_items" if item_type == "found" else "lost_items"
    if item_type == "all":
        # Search both collections
        pass
    
    query = {"status": ItemStatus.ACTIVE}
    if category:
        query["category"] = category
    
    # Get items
    cursor = db[collection].find(query).limit(100)
    items = await cursor.to_list(length=100)
    
    # Simulate similarity scoring (in production, use actual embeddings)
    results = []
    for item in items:
        # Placeholder: random similarity score
        # In production: actual cosine similarity with embeddings
        similarity_score = 0.5  # Placeholder
        
        result = {
            "item": item,
            "similarity_score": similarity_score,
            "match_type": "image",
        }
        results.append(result)
    
    # Sort by similarity score
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    results = results[:limit]
    
    # Convert to response format
    response = []
    for result in results:
        item = result["item"]
        response.append({
            "id": str(item["_id"]),
            "title": item["title"],
            "description": item["description"],
            "category": item["category"],
            "images": item.get("images", []),
            "similarity_score": result["similarity_score"],
            "match_type": result["match_type"],
        })
    
    return {
        "search_image": image_url,
        "total_matches": len(response),
        "matches": response,
    }


@router.post("/text")
async def search_by_text(
    query_text: str = Query(..., min_length=3),
    category: Optional[ItemCategory] = None,
    color: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    item_type: str = Query("found", regex="^(lost|found|all)$"),
    current_user: dict = Depends(get_current_user),
):
    """
    Search items by text description
    """
    db = get_database()
    
    # Build text search query
    search_query = {
        "$or": [
            {"title": {"$regex": query_text, "$options": "i"}},
            {"description": {"$regex": query_text, "$options": "i"}},
            {"color": {"$regex": query_text, "$options": "i"}},
            {"brand": {"$regex": query_text, "$options": "i"}},
        ],
        "status": ItemStatus.ACTIVE,
    }
    
    if category:
        search_query["category"] = category
    if color:
        search_query["color"] = {"$regex": color, "$options": "i"}
    
    # Determine collection(s)
    collections = []
    if item_type == "found" or item_type == "all":
        collections.append("found_items")
    if item_type == "lost" or item_type == "all":
        collections.append("lost_items")
    
    # Search in all collections
    all_results = []
    for collection_name in collections:
        cursor = db[collection_name].find(search_query).limit(limit)
        items = await cursor.to_list(length=limit)
        
        for item in items:
            all_results.append({
                "id": str(item["_id"]),
                "title": item["title"],
                "description": item["description"],
                "category": item["category"],
                "images": item.get("images", []),
                "similarity_score": 0.8,  # Placeholder
                "match_type": "text",
                "collection": collection_name,
            })
    
    return {
        "query": query_text,
        "total_matches": len(all_results),
        "matches": all_results[:limit],
    }


@router.get("/nearby")
async def search_nearby(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius: float = Query(1000, description="Radius in meters"),
    category: Optional[ItemCategory] = None,
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    Search for items near a location
    """
    db = get_database()
    
    # Build geospatial query
    query = {
        "location": {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                },
                "$maxDistance": radius,
            }
        },
        "status": ItemStatus.ACTIVE,
    }
    
    if category:
        query["category"] = category
    
    # Search both collections
    all_results = []
    
    for collection_name in ["found_items", "lost_items"]:
        cursor = db[collection_name].find(query).limit(limit)
        items = await cursor.to_list(length=limit)
        
        for item in items:
            all_results.append({
                "id": str(item["_id"]),
                "title": item["title"],
                "description": item["description"],
                "category": item["category"],
                "images": item.get("images", []),
                "location": item.get("location"),
                "distance": 100,  # Placeholder - calculate actual distance
                "collection": collection_name,
            })
    
    return {
        "search_location": {"latitude": latitude, "longitude": longitude},
        "radius_meters": radius,
        "total_matches": len(all_results),
        "matches": all_results[:limit],
    }


@router.get("/matches/{item_id}")
async def get_item_matches(
    item_id: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """
    Get potential matches for a specific item
    """
    db = get_database()
    
    try:
        object_id = str_to_object_id(item_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID",
        )
    
    # Find the item (check both collections)
    lost_item = await db.lost_items.find_one({"_id": object_id})
    found_item = await db.found_items.find_one({"_id": object_id})
    
    if not lost_item and not found_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )
    
    # Determine search direction
    if lost_item:
        # User lost this item, search in found_items
        source_item = lost_item
        search_collection = "found_items"
    else:
        # User found this item, search in lost_items
        source_item = found_item
        search_collection = "lost_items"
    
    # Build search query based on item attributes
    query = {
        "status": ItemStatus.ACTIVE,
        "$or": [
            {"category": source_item["category"]},
        ],
    }
    
    # Add color to search if available
    if source_item.get("color"):
        query["$or"].append({"color": {"$regex": source_item["color"], "$options": "i"}})
    
    # Search for potential matches
    cursor = db[search_collection].find(query).limit(100)
    potential_matches = await cursor.to_list(length=100)
    
    # Calculate similarity scores (simplified version)
    matches = []
    for match in potential_matches:
        # Calculate text similarity
        score = 0.5  # Placeholder - use actual ML similarity
        
        matches.append({
            "id": str(match["_id"]),
            "title": match["title"],
            "description": match["description"],
            "category": match["category"],
            "images": match.get("images", []),
            "similarity_score": score,
            "match_type": "auto",
        })
    
    # Sort by similarity score
    matches.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    # Update match count
    update_field = "match_count" if not lost_item else "match_count"
    await db[search_collection].update_one(
        {"_id": object_id},
        {"$inc": {"match_count": len(matches)}},
    )
    
    return {
        "item_id": item_id,
        "item_type": "lost" if lost_item else "found",
        "total_matches": len(matches),
        "matches": matches[:limit],
    }


@router.get("/categories")
async def get_categories():
    """
    Get all available item categories
    """
    categories = [
        {"value": cat.value, "label": cat.value.replace("_", " ").title()}
        for cat in ItemCategory
    ]
    return {"categories": categories}

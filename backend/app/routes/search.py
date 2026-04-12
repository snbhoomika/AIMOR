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
from app.utils.file_handler import process_image_to_base64
from app.utils.image_features import get_feature_extractor
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
    item_type: str = Query("all", regex="^(lost|found|all)$"),
    current_user: dict = Depends(get_current_user),
):
    """
    Search for matching items by uploading an image using ML-based similarity matching.
    Uses CLIP ViT-B/32 to extract image features and matches against stored embeddings.
    """
    db = get_database()
    
    # Read and process the uploaded image
    image_content = await image.read()
    
    # Extract features from the search image using CLIP
    extractor = get_feature_extractor()
    search_features = extractor.extract_image_features(image_content)
    
    # Build query
    query = {"status": "active", "image_embedding": {"$exists": True, "$ne": []}}
    if category:
        query["category"] = category
    
    # Determine which collections to search
    collections_to_search = []
    if item_type == "found" or item_type == "all":
        collections_to_search.append("found_items")
    if item_type == "lost" or item_type == "all":
        collections_to_search.append("lost_items")
    
    # Search for matching items
    results = []
    for collection_name in collections_to_search:
        cursor = db[collection_name].find(query)
        items = await cursor.to_list(length=100)
        
        for item in items:
            item_embedding = item.get("image_embedding", [])
            if item_embedding:
                # Calculate actual similarity score using ML embeddings
                similarity_score = cosine_similarity(search_features, item_embedding)
                
                # Only include items with reasonable similarity (threshold 0.3)
                if similarity_score > 0.3:
                    results.append({
                        "item": item,
                        "similarity_score": similarity_score,
                        "match_type": "image",
                        "collection": collection_name,
                    })
    
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
            "collection": result["collection"],
        })
    
    return {
        "total_matches": len(response),
        "matches": response,
    }


@router.get("/text")
async def search_by_text(
    query_text: str = Query(..., min_length=3),
    category: Optional[ItemCategory] = None,
    color: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    item_type: str = Query("all", regex="^(lost|found|all)$"),
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
        "status": "active",
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
                "similarity_score": 0.8,
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
        "status": "active",
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
                "distance": 100,
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
    Get potential matches for a specific item using ML-based similarity
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
        source_item = lost_item
        search_collection = "found_items"
    else:
        source_item = found_item
        search_collection = "lost_items"
    
    # Get source embedding
    source_embedding = source_item.get("image_embedding", [])
    
    # If no embedding exists, fall back to text-based matching
    if not source_embedding:
        return await _text_based_matching(source_item, search_collection, db, limit, item_id, lost_item is not None)
    
    # Search for potential matches with embeddings
    query = {
        "status": "active",
        "image_embedding": {"$exists": True, "$ne": []},
        "_id": {"$ne": object_id},
    }
    
    cursor = db[search_collection].find(query)
    potential_matches = await cursor.to_list(length=100)
    
    # Calculate similarity scores using ML embeddings
    matches = []
    extractor = get_feature_extractor()
    
    for match in potential_matches:
        match_embedding = match.get("image_embedding", [])
        if match_embedding:
            score = cosine_similarity(source_embedding, match_embedding)
            
            # Only include matches above threshold
            if score > 0.3:
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
    matches = matches[:limit]
    
    # Update match count
    await db[search_collection].update_one(
        {"_id": object_id},
        {"$set": {"match_count": len(matches), "updated_at": datetime.utcnow()}},
    )
    
    return {
        "item_id": item_id,
        "item_type": "lost" if lost_item else "found",
        "total_matches": len(matches),
        "matches": matches,
    }


async def _text_based_matching(source_item, search_collection, db, limit, item_id, is_lost):
    """Fallback text-based matching when no image embedding exists"""
    query = {
        "status": "active",
        "$or": [
            {"category": source_item["category"]},
        ],
    }
    
    if source_item.get("color"):
        query["$or"].append({"color": {"$regex": source_item["color"], "$options": "i"}})
    
    cursor = db[search_collection].find(query)
    potential_matches = await cursor.to_list(length=100)
    
    matches = []
    for match in potential_matches:
        matches.append({
            "id": str(match["_id"]),
            "title": match["title"],
            "description": match["description"],
            "category": match["category"],
            "images": match.get("images", []),
            "similarity_score": 0.5,
            "match_type": "category",
        })
    
    return {
        "item_id": item_id,
        "item_type": "lost" if is_lost else "found",
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

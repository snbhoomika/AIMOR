from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
import json

from app.models.item import (
    LostItemCreate,
    LostItemResponse,
    LostItemInDB,
    ItemUpdate,
    ItemStatus,
    ItemCategory,
)
from app.models.notification import NotificationCreate, NotificationType
from app.utils.security import get_current_user, str_to_object_id
from app.utils.file_handler import save_multiple_files, save_multiple_images_as_base64, delete_file
from app.core.database import get_database

router = APIRouter(prefix="/lost-items", tags=["Lost Items"])


@router.post("/", response_model=LostItemResponse, status_code=status.HTTP_201_CREATED)
async def create_lost_item(
    title: str = Form(...),
    description: str = Form(...),
    category: ItemCategory = Form(...),
    date: str = Form(...),
    color: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    distinguishing_features: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    images: List[UploadFile] = File([]),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new lost item report
    """
    db = get_database()

    # Parse date
    try:
        parsed_date = datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
        )

    # Upload images as base64 with ML features
    image_urls = []
    image_features = []
    if images:
        image_urls, image_features = await save_multiple_images_as_base64(images)

    # Create item document
    item_data = {
        "title": title,
        "description": description,
        "category": category,
        "date": parsed_date,
        "color": color,
        "brand": brand,
        "distinguishing_features": distinguishing_features,
        "images": image_urls,
        "image_embedding": image_features,
        "user_id": str(current_user["_id"]),
        "status": ItemStatus.ACTIVE,
        "views": 0,
        "match_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=90),  # Auto-expire after 90 days
    }

    # Add location if provided
    if latitude and longitude:
        item_data["location"] = {
            "type": "Point",
            "coordinates": [longitude, latitude],
            "address": location,
        }
    elif location:
        item_data["location"] = {
            "type": "Point",
            "coordinates": [0, 0],  # Default, should be geocoded
            "address": location,
        }

    # Insert into database
    result = await db.lost_items.insert_one(item_data)
    item_id = str(result.inserted_id)

    # TODO: Trigger ML feature extraction for the image

    # Return response
    return LostItemResponse(
        id=item_id,
        title=title,
        description=description,
        category=category,
        date=parsed_date,
        color=color,
        brand=brand,
        distinguishing_features=distinguishing_features,
        location=item_data.get("location"),
        images=image_urls,
        user_id=str(current_user["_id"]),
        status=ItemStatus.ACTIVE,
        views=0,
        match_count=0,
        created_at=item_data["created_at"],
    )


@router.get("/", response_model=List[LostItemResponse])
async def get_lost_items(
    category: Optional[ItemCategory] = None,
    status: Optional[ItemStatus] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    Get all lost items (with pagination and filters)
    """
    db = get_database()

    # Build query
    query = {}
    if category:
        query["category"] = category
    if status:
        query["status"] = status

    # Calculate skip
    skip = (page - 1) * limit

    # Get items
    cursor = db.lost_items.find(query).sort("created_at", -1).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)

    # Convert to response
    response = []
    for item in items:
        response.append(
            LostItemResponse(
                id=str(item["_id"]),
                title=item["title"],
                description=item["description"],
                category=item["category"],
                date=item["date"],
                color=item.get("color"),
                brand=item.get("brand"),
                distinguishing_features=item.get("distinguishing_features"),
                location=item.get("location"),
                images=item.get("images", []),
                user_id=item["user_id"],
                status=item["status"],
                views=item.get("views", 0),
                match_count=item.get("match_count", 0),
                created_at=item["created_at"],
            )
        )

    return response


@router.get("/my", response_model=List[LostItemResponse])
async def get_my_lost_items(
    status: Optional[ItemStatus] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Get current user's lost items
    """
    db = get_database()

    query = {"user_id": str(current_user["_id"])}
    if status:
        query["status"] = status

    cursor = db.lost_items.find(query).sort("created_at", -1)
    items = await cursor.to_list(length=100)

    response = []
    for item in items:
        response.append(
            LostItemResponse(
                id=str(item["_id"]),
                title=item["title"],
                description=item["description"],
                category=item["category"],
                date=item["date"],
                color=item.get("color"),
                brand=item.get("brand"),
                distinguishing_features=item.get("distinguishing_features"),
                location=item.get("location"),
                images=item.get("images", []),
                user_id=item["user_id"],
                status=item["status"],
                views=item.get("views", 0),
                match_count=item.get("match_count", 0),
                created_at=item["created_at"],
            )
        )

    return response


@router.get("/{item_id}", response_model=LostItemResponse)
async def get_lost_item(
    item_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get a specific lost item by ID
    """
    db = get_database()

    try:
        object_id = str_to_object_id(item_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID",
        )

    item = await db.lost_items.find_one({"_id": object_id})

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    # Increment views
    await db.lost_items.update_one(
        {"_id": object_id},
        {"$inc": {"views": 1}},
    )

    return LostItemResponse(
        id=str(item["_id"]),
        title=item["title"],
        description=item["description"],
        category=item["category"],
        date=item["date"],
        color=item.get("color"),
        brand=item.get("brand"),
        distinguishing_features=item.get("distinguishing_features"),
        location=item.get("location"),
        images=item.get("images", []),
        user_id=item["user_id"],
        status=item["status"],
        views=item.get("views", 0) + 1,
        match_count=item.get("match_count", 0),
        created_at=item["created_at"],
    )


@router.put("/{item_id}", response_model=LostItemResponse)
async def update_lost_item(
    item_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category: Optional[ItemCategory] = Form(None),
    color: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    distinguishing_features: Optional[str] = Form(None),
    status: Optional[ItemStatus] = Form(None),
    new_images: List[UploadFile] = File([]),
    current_user: dict = Depends(get_current_user),
):
    """
    Update a lost item
    """
    db = get_database()

    try:
        object_id = str_to_object_id(item_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID",
        )

    # Check ownership
    item = await db.lost_items.find_one({"_id": object_id})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    if item["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item",
        )

    # Build update data
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if category is not None:
        update_data["category"] = category
    if color is not None:
        update_data["color"] = color
    if brand is not None:
        update_data["brand"] = brand
    if distinguishing_features is not None:
        update_data["distinguishing_features"] = distinguishing_features
    if status is not None:
        update_data["status"] = status

    # Upload new images
    if new_images:
        new_urls = await save_multiple_files(new_images, subfolder="lost-items")
        update_data["$addToSet"] = {"images": {"$each": new_urls}}

    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.lost_items.update_one({"_id": object_id}, {"$set": update_data})

    # Get updated item
    updated_item = await db.lost_items.find_one({"_id": object_id})

    return LostItemResponse(
        id=str(updated_item["_id"]),
        title=updated_item["title"],
        description=updated_item["description"],
        category=updated_item["category"],
        date=updated_item["date"],
        color=updated_item.get("color"),
        brand=updated_item.get("brand"),
        distinguishing_features=updated_item.get("distinguishing_features"),
        location=updated_item.get("location"),
        images=updated_item.get("images", []),
        user_id=updated_item["user_id"],
        status=updated_item["status"],
        views=updated_item.get("views", 0),
        match_count=updated_item.get("match_count", 0),
        created_at=updated_item["created_at"],
    )


@router.delete("/{item_id}")
async def delete_lost_item(
    item_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a lost item
    """
    db = get_database()

    try:
        object_id = str_to_object_id(item_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID",
        )

    # Check ownership
    item = await db.lost_items.find_one({"_id": object_id})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    if item["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item",
        )

    # Delete images
    for image_url in item.get("images", []):
        delete_file(image_url)

    # Delete item
    await db.lost_items.delete_one({"_id": object_id})

    return {"message": "Item deleted successfully"}


@router.post("/{item_id}/mark-returned")
async def mark_item_returned(
    item_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Mark a lost item as returned
    """
    db = get_database()

    try:
        object_id = str_to_object_id(item_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID",
        )

    # Check ownership
    item = await db.lost_items.find_one({"_id": object_id})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    if item["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item",
        )

    # Update status
    await db.lost_items.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": ItemStatus.RETURNED,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    return {"message": "Item marked as returned"}

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.models.notification import (
    NotificationResponse,
    NotificationUpdate,
    NotificationType,
)
from app.utils.security import get_current_user, str_to_object_id
from app.core.database import get_database

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    Get notifications for current user
    """
    db = get_database()

    query = {"user_id": str(current_user["_id"])}
    if unread_only:
        query["read"] = False

    cursor = db.notifications.find(query).sort("created_at", -1).limit(limit)
    notifications = await cursor.to_list(length=limit)

    response = []
    for notif in notifications:
        response.append(
            NotificationResponse(
                id=str(notif["_id"]),
                user_id=notif["user_id"],
                type=notif["type"],
                title=notif["title"],
                message=notif["message"],
                data=notif.get("data"),
                read=notif.get("read", False),
                created_at=notif["created_at"],
            )
        )

    return response


@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
):
    """
    Get count of unread notifications
    """
    db = get_database()

    count = await db.notifications.count_documents({
        "user_id": str(current_user["_id"]),
        "read": False,
    })

    return {"unread_count": count}


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Mark a notification as read
    """
    db = get_database()

    try:
        object_id = str_to_object_id(notification_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID",
        )

    # Check ownership
    notification = await db.notifications.find_one({"_id": object_id})
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if notification["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this notification",
        )

    # Update notification
    await db.notifications.update_one(
        {"_id": object_id},
        {"$set": {"read": True}},
    )

    return {"message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
):
    """
    Mark all notifications as read
    """
    db = get_database()

    result = await db.notifications.update_many(
        {
            "user_id": str(current_user["_id"]),
            "read": False,
        },
        {"$set": {"read": True}},
    )

    return {
        "message": "All notifications marked as read",
        "updated_count": result.modified_count,
    }


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a notification
    """
    db = get_database()

    try:
        object_id = str_to_object_id(notification_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID",
        )

    # Check ownership
    notification = await db.notifications.find_one({"_id": object_id})
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if notification["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this notification",
        )

    # Delete notification
    await db.notifications.delete_one({"_id": object_id})

    return {"message": "Notification deleted"}


@router.delete("/clear-all")
async def clear_all_notifications(
    current_user: dict = Depends(get_current_user),
):
    """
    Clear all notifications for current user
    """
    db = get_database()

    result = await db.notifications.delete_many({
        "user_id": str(current_user["_id"]),
    })

    return {
        "message": "All notifications cleared",
        "deleted_count": result.deleted_count,
    }

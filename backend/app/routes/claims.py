from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.models.claim import (
    ClaimCreate,
    ClaimResponse,
    ClaimUpdate,
    ClaimStatus,
    ClaimQuestion,
)
from app.models.notification import NotificationCreate, NotificationType
from app.models.item import ItemStatus
from app.utils.security import get_current_user, str_to_object_id
from app.core.database import get_database

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.post("/", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim(
    claim_data: ClaimCreate = Body(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new claim for a lost item
    """
    db = get_database()

    # Validate IDs
    try:
        lost_item_id = str_to_object_id(claim_data.lost_item_id)
        found_item_id = str_to_object_id(claim_data.found_item_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID",
        )

    # Check if items exist
    lost_item = await db.lost_items.find_one({"_id": lost_item_id})
    found_item = await db.found_items.find_one({"_id": found_item_id})

    if not lost_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lost item not found",
        )

    if not found_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Found item not found",
        )

    # Check if user is trying to claim their own found item
    if found_item["user_id"] == str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot claim your own found item",
        )

    # Check if claim already exists
    existing_claim = await db.claims.find_one({
        "lost_item_id": claim_data.lost_item_id,
        "found_item_id": claim_data.found_item_id,
        "claimant_id": str(current_user["_id"]),
        "status": {"$in": [ClaimStatus.PENDING, ClaimStatus.ACCEPTED]},
    })

    if existing_claim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claim already exists",
        )

    # Create claim document
    claim_dict = claim_data.model_dump()
    claim_dict["claimant_id"] = str(current_user["_id"])
    claim_dict["owner_id"] = found_item["user_id"]
    claim_dict["status"] = ClaimStatus.PENDING
    claim_dict["created_at"] = datetime.utcnow()
    claim_dict["updated_at"] = datetime.utcnow()

    # Insert claim
    result = await db.claims.insert_one(claim_dict)
    claim_id = str(result.inserted_id)

    # Create notification for found item owner
    notification = NotificationCreate(
        user_id=found_item["user_id"],
        type=NotificationType.CLAIM_RECEIVED,
        title="New Claim Received",
        message=f"Someone claimed your found item: {found_item['title']}",
        data={
            "claim_id": claim_id,
            "lost_item_id": claim_data.lost_item_id,
            "found_item_id": claim_data.found_item_id,
        },
    )
    await db.notifications.insert_one(notification.model_dump())

    # Return response
    return ClaimResponse(
        id=claim_id,
        lost_item_id=claim_data.lost_item_id,
        found_item_id=claim_data.found_item_id,
        message=claim_data.message,
        verification_questions=claim_data.verification_questions,
        claimant_id=str(current_user["_id"]),
        owner_id=found_item["user_id"],
        status=ClaimStatus.PENDING,
        similarity_score=None,
        created_at=claim_dict["created_at"],
    )


@router.get("/my-claims", response_model=List[ClaimResponse])
async def get_my_claims(
    status: Optional[ClaimStatus] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Get claims made by current user (as claimant)
    """
    db = get_database()

    query = {"claimant_id": str(current_user["_id"])}
    if status:
        query["status"] = status

    cursor = db.claims.find(query).sort("created_at", -1)
    claims = await cursor.to_list(length=100)

    response = []
    for claim in claims:
        response.append(
            ClaimResponse(
                id=str(claim["_id"]),
                lost_item_id=claim["lost_item_id"],
                found_item_id=claim["found_item_id"],
                message=claim["message"],
                verification_questions=claim.get("verification_questions"),
                claimant_id=claim["claimant_id"],
                owner_id=claim["owner_id"],
                status=claim["status"],
                similarity_score=claim.get("similarity_score"),
                response_message=claim.get("response_message"),
                created_at=claim["created_at"],
            )
        )

    return response


@router.get("/incoming", response_model=List[ClaimResponse])
async def get_incoming_claims(
    status: Optional[ClaimStatus] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Get claims made to current user's found items (as owner)
    """
    db = get_database()

    query = {"owner_id": str(current_user["_id"])}
    if status:
        query["status"] = status

    cursor = db.claims.find(query).sort("created_at", -1)
    claims = await cursor.to_list(length=100)

    response = []
    for claim in claims:
        response.append(
            ClaimResponse(
                id=str(claim["_id"]),
                lost_item_id=claim["lost_item_id"],
                found_item_id=claim["found_item_id"],
                message=claim["message"],
                verification_questions=claim.get("verification_questions"),
                claimant_id=claim["claimant_id"],
                owner_id=claim["owner_id"],
                status=claim["status"],
                similarity_score=claim.get("similarity_score"),
                response_message=claim.get("response_message"),
                created_at=claim["created_at"],
            )
        )

    return response


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get a specific claim by ID
    """
    db = get_database()

    try:
        object_id = str_to_object_id(claim_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid claim ID",
        )

    claim = await db.claims.find_one({"_id": object_id})

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    # Check if user is involved in this claim
    if claim["claimant_id"] != str(current_user["_id"]) and claim["owner_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this claim",
        )

    return ClaimResponse(
        id=str(claim["_id"]),
        lost_item_id=claim["lost_item_id"],
        found_item_id=claim["found_item_id"],
        message=claim["message"],
        verification_questions=claim.get("verification_questions"),
        claimant_id=claim["claimant_id"],
        owner_id=claim["owner_id"],
        status=claim["status"],
        similarity_score=claim.get("similarity_score"),
        response_message=claim.get("response_message"),
        created_at=claim["created_at"],
    )


@router.put("/{claim_id}/accept")
async def accept_claim(
    claim_id: str,
    response_message: Optional[str] = Body(None),
    meeting_location: Optional[str] = Body(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Accept a claim (owner only)
    """
    db = get_database()

    try:
        object_id = str_to_object_id(claim_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid claim ID",
        )

    claim = await db.claims.find_one({"_id": object_id})

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    # Check ownership
    if claim["owner_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the found item owner can accept claims",
        )

    # Check if claim is pending
    if claim["status"] != ClaimStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claim is not pending",
        )

    # Update claim status
    update_data = {
        "status": ClaimStatus.ACCEPTED,
        "response_message": response_message,
        "updated_at": datetime.utcnow(),
    }
    if meeting_location:
        update_data["meeting_location"] = meeting_location

    await db.claims.update_one({"_id": object_id}, {"$set": update_data})

    # Update item statuses
    await db.lost_items.update_one(
        {"_id": ObjectId(claim["lost_item_id"])},
        {"$set": {"status": ItemStatus.MATCHED, "updated_at": datetime.utcnow()}},
    )
    await db.found_items.update_one(
        {"_id": ObjectId(claim["found_item_id"])},
        {"$set": {"status": ItemStatus.MATCHED, "updated_at": datetime.utcnow()}},
    )

    # Create notification for claimant
    notification = NotificationCreate(
        user_id=claim["claimant_id"],
        type=NotificationType.CLAIM_ACCEPTED,
        title="Claim Accepted",
        message=f"Your claim has been accepted!",
        data={
            "claim_id": claim_id,
            "meeting_location": meeting_location,
        },
    )
    await db.notifications.insert_one(notification.model_dump())

    return {"message": "Claim accepted successfully"}


@router.put("/{claim_id}/reject")
async def reject_claim(
    claim_id: str,
    response_message: Optional[str] = Body(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Reject a claim (owner only)
    """
    db = get_database()

    try:
        object_id = str_to_object_id(claim_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid claim ID",
        )

    claim = await db.claims.find_one({"_id": object_id})

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    # Check ownership
    if claim["owner_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the found item owner can reject claims",
        )

    # Check if claim is pending
    if claim["status"] != ClaimStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claim is not pending",
        )

    # Update claim status
    await db.claims.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": ClaimStatus.REJECTED,
                "response_message": response_message,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    # Create notification for claimant
    notification = NotificationCreate(
        user_id=claim["claimant_id"],
        type=NotificationType.CLAIM_REJECTED,
        title="Claim Rejected",
        message=f"Your claim has been rejected." + (f" Reason: {response_message}" if response_message else ""),
        data={"claim_id": claim_id},
    )
    await db.notifications.insert_one(notification.model_dump())

    return {"message": "Claim rejected successfully"}


@router.put("/{claim_id}/complete")
async def complete_claim(
    claim_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Mark a claim as completed (item returned)
    """
    db = get_database()

    try:
        object_id = str_to_object_id(claim_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid claim ID",
        )

    claim = await db.claims.find_one({"_id": object_id})

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found",
        )

    # Check if user is involved in this claim
    if claim["claimant_id"] != str(current_user["_id"]) and claim["owner_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this claim",
        )

    # Check if claim is accepted
    if claim["status"] != ClaimStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Claim must be accepted before completing",
        )

    # Update claim status
    await db.claims.update_one(
        {"_id": object_id},
        {
            "$set": {
                "status": ClaimStatus.COMPLETED,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    # Update item statuses
    await db.lost_items.update_one(
        {"_id": ObjectId(claim["lost_item_id"])},
        {"$set": {"status": ItemStatus.RETURNED, "updated_at": datetime.utcnow()}},
    )
    await db.found_items.update_one(
        {"_id": ObjectId(claim["found_item_id"])},
        {"$set": {"status": ItemStatus.RETURNED, "updated_at": datetime.utcnow()}},
    )

    # Create notifications for both parties
    notification_claimant = NotificationCreate(
        user_id=claim["claimant_id"],
        type=NotificationType.ITEM_RETURNED,
        title="Item Returned",
        message="Great news! Your item has been returned.",
        data={"claim_id": claim_id},
    )
    await db.notifications.insert_one(notification_claimant.model_dump())

    notification_owner = NotificationCreate(
        user_id=claim["owner_id"],
        type=NotificationType.ITEM_RETURNED,
        title="Item Returned",
        message="Thank you! The item has been returned to its owner.",
        data={"claim_id": claim_id},
    )
    await db.notifications.insert_one(notification_owner.model_dump())

    return {"message": "Claim completed successfully"}

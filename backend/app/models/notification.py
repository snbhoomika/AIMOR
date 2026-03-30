from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    MATCH_FOUND = "match_found"
    CLAIM_RECEIVED = "claim_received"
    CLAIM_ACCEPTED = "claim_accepted"
    CLAIM_REJECTED = "claim_rejected"
    ITEM_RETURNED = "item_returned"
    SYSTEM = "system"


class NotificationBase(BaseModel):
    user_id: str
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None  # Additional data (item_id, claim_id, etc.)


class NotificationCreate(NotificationBase):
    pass


class NotificationInDB(NotificationBase):
    id: str = Field(alias="_id")
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class NotificationResponse(NotificationBase):
    id: str
    read: bool
    created_at: datetime


class NotificationUpdate(BaseModel):
    read: Optional[bool] = None

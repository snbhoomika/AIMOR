from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ClaimStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ClaimQuestion(BaseModel):
    question: str
    answer: str


class ClaimBase(BaseModel):
    lost_item_id: str
    found_item_id: str
    message: str = Field(..., min_length=10, max_length=1000)
    verification_questions: Optional[list[ClaimQuestion]] = None


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdate(BaseModel):
    status: Optional[ClaimStatus] = None
    response_message: Optional[str] = None


class ClaimInDB(ClaimBase):
    id: str = Field(alias="_id")
    claimant_id: str  # User who lost the item
    owner_id: str  # User who found the item
    status: ClaimStatus = ClaimStatus.PENDING
    similarity_score: Optional[float] = None
    response_message: Optional[str] = None
    meeting_location: Optional[str] = None
    meeting_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ClaimResponse(ClaimBase):
    id: str
    claimant_id: str
    owner_id: str
    status: ClaimStatus
    similarity_score: Optional[float]
    response_message: Optional[str]
    created_at: datetime

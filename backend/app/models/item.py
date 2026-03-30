from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ItemCategory(str, Enum):
    BAG = "bag"
    WALLET = "wallet"
    PHONE = "phone"
    KEYS = "keys"
    BOTTLE = "bottle"
    LAPTOP = "laptop"
    ID_CARD = "id_card"
    UMBRELLA = "umbrella"
    WATCH = "watch"
    EARPHONES = "earphones"
    BOOKS = "books"
    OTHERS = "others"


class ItemStatus(str, Enum):
    ACTIVE = "active"
    MATCHED = "matched"
    CLAIMED = "claimed"
    RETURNED = "returned"
    EXPIRED = "expired"


class Location(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]
    address: Optional[str] = None
    place_name: Optional[str] = None


class ItemBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category: ItemCategory
    color: Optional[str] = None
    brand: Optional[str] = None
    distinguishing_features: Optional[str] = None
    location: Optional[Location] = None
    date: datetime  # Date when item was lost/found


class LostItemCreate(ItemBase):
    pass


class FoundItemCreate(ItemBase):
    current_location: Optional[str] = None  # Where item is being kept


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[ItemCategory] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    distinguishing_features: Optional[str] = None
    location: Optional[Location] = None
    status: Optional[ItemStatus] = None


class LostItemInDB(ItemBase):
    id: str = Field(alias="_id")
    user_id: str
    images: List[str] = []  # URLs to uploaded images
    image_embeddings: Optional[List[float]] = None  # ML feature vector
    status: ItemStatus = ItemStatus.ACTIVE
    views: int = 0
    match_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class FoundItemInDB(ItemBase):
    id: str = Field(alias="_id")
    user_id: str
    images: List[str] = []
    image_embeddings: Optional[List[float]] = None
    current_location: Optional[str] = None
    status: ItemStatus = ItemStatus.ACTIVE
    is_verified: bool = False  # Admin verification
    views: int = 0
    match_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ItemResponse(ItemBase):
    id: str
    user_id: str
    images: List[str]
    status: ItemStatus
    views: int
    created_at: datetime


class LostItemResponse(ItemResponse):
    match_count: int


class FoundItemResponse(ItemResponse):
    current_location: Optional[str]
    is_verified: bool
    match_count: int


class ItemSearchParams(BaseModel):
    query: Optional[str] = None
    category: Optional[ItemCategory] = None
    color: Optional[str] = None
    location: Optional[Location] = None
    radius: Optional[float] = 1000  # meters
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: ItemStatus = ItemStatus.ACTIVE
    page: int = 1
    limit: int = 20

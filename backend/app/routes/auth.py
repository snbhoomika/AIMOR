from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer
from bson import ObjectId
from datetime import datetime
from typing import Optional

from app.models.user import (
    UserCreate,
    UserResponse,
    UserUpdate,
    Token,
    UserInDB,
)
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_user_token,
    get_current_user,
    str_to_object_id,
)
from app.core.database import get_database

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate = Body(...)):
    """
    Register a new user
    """
    db = get_database()

    # Check if email already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user document
    user_dict = user_data.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["is_active"] = True
    user_dict["is_verified"] = False

    # Insert user
    result = await db.users.insert_one(user_dict)
    user_id = str(result.inserted_id)

    # Generate token
    token = create_user_token(user_id, user_data.email)

    # Prepare response
    user_response = UserResponse(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        is_active=True,
        is_verified=False,
        created_at=user_dict["created_at"],
    )

    return Token(
        access_token=token,
        user=user_response,
    )


@router.post("/login", response_model=Token)
async def login(
    email: str = Body(...),
    password: str = Body(...),
):
    """
    Login user and return token
    """
    db = get_database()

    # Find user by email
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Verify password
    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}},
    )

    # Generate token
    user_id = str(user["_id"])
    token = create_user_token(user_id, email)

    # Prepare response
    user_response = UserResponse(
        id=user_id,
        email=user["email"],
        full_name=user["full_name"],
        phone=user.get("phone"),
        role=user.get("role", "user"),
        is_active=user.get("is_active", True),
        is_verified=user.get("is_verified", False),
        avatar=user.get("avatar"),
        created_at=user["created_at"],
    )

    return Token(
        access_token=token,
        user=user_response,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    """
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        full_name=current_user["full_name"],
        phone=current_user.get("phone"),
        role=current_user.get("role", "user"),
        is_active=current_user.get("is_active", True),
        is_verified=current_user.get("is_verified", False),
        avatar=current_user.get("avatar"),
        created_at=current_user["created_at"],
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate = Body(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Update current user information
    """
    db = get_database()

    # Prepare update data
    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    # Update user
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_data},
    )

    # Get updated user
    updated_user = await db.users.find_one({"_id": current_user["_id"]})

    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        full_name=updated_user["full_name"],
        phone=updated_user.get("phone"),
        role=updated_user.get("role", "user"),
        is_active=updated_user.get("is_active", True),
        is_verified=updated_user.get("is_verified", False),
        avatar=updated_user.get("avatar"),
        created_at=updated_user["created_at"],
    )


@router.post("/change-password")
async def change_password(
    current_password: str = Body(...),
    new_password: str = Body(..., min_length=6),
    current_user: dict = Depends(get_current_user),
):
    """
    Change user password
    """
    db = get_database()

    # Verify current password
    if not verify_password(current_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    # Update password
    hashed_password = get_password_hash(new_password)
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "hashed_password": hashed_password,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    return {"message": "Password updated successfully"}


@router.post("/logout")
async def logout():
    """
    Logout user (client should delete token)
    Note: For true logout, implement token blacklisting
    """
    return {"message": "Logout successful. Please delete the token on client side."}

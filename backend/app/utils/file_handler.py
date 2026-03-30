import os
import uuid
from typing import List, Optional
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io

from app.core.config import settings


# Ensure upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def validate_image_file(file: UploadFile) -> bool:
    """Validate that uploaded file is an allowed image type"""
    # Check file extension
    if file.filename:
        ext = file.filename.split(".")[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            return False

    # Check content type
    allowed_content_types = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    ]
    if file.content_type not in allowed_content_types:
        return False

    return True


async def save_upload_file(
    file: UploadFile,
    subfolder: str = "items",
    resize: bool = True,
    max_size: tuple = (1024, 1024),
) -> str:
    """
    Save an uploaded file and return the URL path

    Args:
        file: The uploaded file
        subfolder: Subfolder to save in (e.g., 'items', 'avatars')
        resize: Whether to resize the image
        max_size: Maximum dimensions for resizing

    Returns:
        URL path to the saved file
    """
    # Validate file
    if not await validate_image_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    # Generate unique filename
    ext = file.filename.split(".")[-1].lower() if file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"

    # Create full path
    folder_path = UPLOAD_DIR / subfolder
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path / filename

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB",
        )

    # Process image if needed
    if resize and file.content_type.startswith("image/"):
        try:
            image = Image.open(io.BytesIO(content))

            # Convert to RGB if necessary
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # Resize while maintaining aspect ratio
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save processed image
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85)
            content = buffer.getvalue()
            file_path = file_path.with_suffix(".jpg")
        except Exception as e:
            # If image processing fails, save original
            pass

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Return URL path
    return f"/uploads/{subfolder}/{filename}"


async def save_multiple_files(
    files: List[UploadFile],
    subfolder: str = "items",
    max_files: int = 5,
) -> List[str]:
    """Save multiple files and return list of URLs"""
    if len(files) > max_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {max_files} files allowed",
        )

    urls = []
    for file in files:
        if file.filename:  # Skip empty files
            url = await save_upload_file(file, subfolder)
            urls.append(url)

    return urls


def delete_file(file_path: str) -> bool:
    """Delete a file from the upload directory"""
    try:
        # Convert URL path to file system path
        if file_path.startswith("/uploads/"):
            relative_path = file_path[1:]  # Remove leading /
            full_path = Path(relative_path)

            if full_path.exists():
                full_path.unlink()
                return True
    except Exception:
        pass
    return False


def get_file_url(file_path: str, base_url: str = "") -> str:
    """Get full URL for a file"""
    if file_path.startswith("http"):
        return file_path
    return f"{base_url}{file_path}"


async def compress_image(image_data: bytes, quality: int = 85) -> bytes:
    """Compress image data"""
    try:
        image = Image.open(io.BytesIO(image_data))
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality)
        return buffer.getvalue()
    except Exception:
        return image_data

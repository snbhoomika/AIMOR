import os
import uuid
import base64
from typing import List, Optional
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io

from app.core.config import settings


UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def validate_image_file(file: UploadFile) -> bool:
    """Validate that uploaded file is an allowed image type"""
    if file.filename:
        ext = file.filename.split(".")[-1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            return False

    allowed_content_types = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    ]
    if file.content_type not in allowed_content_types:
        return False

    return True


async def process_image_to_base64(file: UploadFile) -> tuple:
    """
    Process an uploaded image and return base64 string and feature vector for storage in database.
    Returns: (base64_string, feature_vector)
    """
    if not await validate_image_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()

    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB",
        )

    try:
        image = Image.open(io.BytesIO(content))

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        processed_content = buffer.getvalue()

        base64_string = base64.b64encode(processed_content).decode("utf-8")
        content_type = "image/jpeg"
        base64_data = f"data:{content_type};base64,{base64_string}"
        
        # Extract features using CLIP model
        from app.utils.image_features import get_feature_extractor
        extractor = get_feature_extractor()
        features = extractor.extract_image_features(processed_content)
        
        return base64_data, features
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process image: {str(e)}",
        )


async def save_multiple_images_as_base64(
    files: List[UploadFile],
    max_files: int = 5,
) -> tuple:
    """
    Process multiple files and return list of base64 data URLs and combined feature vector.
    Returns: (urls, features)
    """
    if len(files) > max_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {max_files} files allowed",
        )

    urls = []
    all_features = []
    for file in files:
        if file.filename:
            url, features = await process_image_to_base64(file)
            urls.append(url)
            all_features.append(features)
    
    # Combine features from all images (average)
    combined_features = []
    if all_features:
        feature_dim = len(all_features[0])
        combined_features = [
            sum(f[i] for f in all_features) / len(all_features)
            for i in range(feature_dim)
        ]

    return urls, combined_features


async def save_upload_file(
    file: UploadFile,
    subfolder: str = "items",
    resize: bool = True,
    max_size: tuple = (1024, 1024),
) -> str:
    """
    Save an uploaded file and return the URL path
    """
    if not await validate_image_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    ext = file.filename.split(".")[-1].lower() if file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"

    folder_path = UPLOAD_DIR / subfolder
    folder_path.mkdir(parents=True, exist_ok=True)
    file_path = folder_path / filename

    content = await file.read()

    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB",
        )

    if resize and file.content_type.startswith("image/"):
        try:
            image = Image.open(io.BytesIO(content))

            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85)
            content = buffer.getvalue()
            file_path = file_path.with_suffix(".jpg")
        except Exception:
            pass

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

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
        if file.filename:
            url = await save_upload_file(file, subfolder)
            urls.append(url)

    return urls


def delete_file(file_path: str) -> bool:
    """Delete a file from the upload directory"""
    try:
        if file_path.startswith("/uploads/"):
            relative_path = file_path[1:]
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

"""File upload and media browsing endpoints."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pathlib import Path
from typing import Optional
import uuid
import shutil
from PIL import Image
from app.config import settings
from app.services.media_scanner import validate_path, scan_directory

router = APIRouter(tags=["uploads"])


@router.post("/api/uploads/logo/{channel_id}")
async def upload_logo(channel_id: str, file: UploadFile = File(...)):
    """
    Upload a channel logo image.

    Args:
        channel_id: ID of the channel
        file: Uploaded image file

    Returns:
        Dictionary with logo_url, filename, and size

    Raises:
        HTTPException: If file is invalid or upload fails
    """
    # Validate file exists
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_logo_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_logo_extensions)}"
        )

    # Read file content
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Validate file size
    file_size = len(contents)
    max_size_bytes = settings.max_logo_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_logo_size_mb}MB"
        )

    # Validate it's a real image using Pillow
    try:
        image = Image.open(file.file)
        image.verify()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Delete old logo files for this channel
    try:
        for old_file in settings.logos_dir.glob(f"{channel_id}_*"):
            old_file.unlink()
    except Exception:
        pass  # Ignore errors deleting old files

    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{channel_id}_{unique_id}{file_ext}"
    file_path = settings.logos_dir / filename

    # Save file
    try:
        # Reset file pointer before saving
        await file.seek(0)
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Return logo URL
    logo_url = f"/logos/{filename}"
    return {
        "logo_url": logo_url,
        "filename": filename,
        "size": file_size
    }


@router.get("/api/media/browse")
async def browse_media(path: Optional[str] = Query(default=None)):
    """
    Browse media directory and list files/folders.

    Args:
        path: Optional relative path within media directory

    Returns:
        Dictionary with current_path, parent_path, and items list

    Raises:
        HTTPException: If path is invalid or inaccessible
    """
    # Validate and resolve path
    validated_path = validate_path(path or '', settings.media_dir)

    # Scan directory
    result = scan_directory(validated_path, settings.media_dir)

    return result


@router.delete("/api/uploads/logo/{channel_id}")
async def delete_logo(channel_id: str):
    """
    Delete logo file(s) for a channel.

    Args:
        channel_id: ID of the channel

    Returns:
        Success message

    Raises:
        HTTPException: If deletion fails
    """
    deleted_count = 0

    try:
        for logo_file in settings.logos_dir.glob(f"{channel_id}_*"):
            logo_file.unlink()
            deleted_count += 1
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete logo: {str(e)}")

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Logo not found")

    return {"message": f"Deleted {deleted_count} logo file(s)"}

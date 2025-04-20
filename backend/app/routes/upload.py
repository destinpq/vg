"""
File upload routes
"""
import os
import uuid
import shutil
import logging
from typing import Dict, List, Any
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from starlette.responses import JSONResponse

from app.utils.config import get_settings
from app.utils.file_utils import ensure_directory

router = APIRouter()
settings = get_settings()

@router.options("/image")
async def options_upload_image():
    """
    Handle OPTIONS request for the upload endpoint
    """
    return Response(status_code=200)

@router.post("/image")
async def upload_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload an image file for image-to-video processing
    
    Args:
        file: The image file to upload
        
    Returns:
        Dict with file path and other info
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file type
    allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Create unique filename with uuid to prevent collisions
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # Create upload directory in output dir
    upload_dir = os.path.join(settings.OUTPUT_DIR, "uploads")
    ensure_directory(upload_dir)
    
    # Full path where the file will be saved
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        # Write file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logging.error(f"Error saving uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    finally:
        file.file.close()
    
    # Return file info
    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "size": os.path.getsize(file_path),
        "content_type": file.content_type
    } 
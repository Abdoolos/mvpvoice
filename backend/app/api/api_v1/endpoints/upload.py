"""
API endpoints for file upload.
Designer: Abdullah Alawiss
"""

import os
import uuid
import aiofiles
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.config import settings
from ....models.call import Call
from ....schemas.call import UploadResponse
from ....workers.audio_tasks import process_audio_file

router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an audio file for processing."""
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported formats: {', '.join(settings.SUPPORTED_AUDIO_FORMATS)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, unique_filename)
    
    try:
        # Save file to disk
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        
        # Validate file size
        if file_size > settings.MAX_CONTENT_LENGTH:
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_CONTENT_LENGTH} bytes"
            )
        
        # Create call record in database
        call = Call(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            format=file_extension,
            status="uploaded"
        )
        
        db.add(call)
        db.commit()
        db.refresh(call)
        
        # Start async processing
        task = process_audio_file.delay(call.id)
        
        return UploadResponse(
            call_id=call.id,
            filename=unique_filename,
            original_filename=file.filename,
            file_size=file_size,
            status="uploaded",
            message=f"File uploaded successfully. Processing started with task ID: {task.id}"
        )
        
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/batch", response_model=List[UploadResponse])
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple audio files for processing."""
    
    if len(files) > 10:  # Limit batch uploads
        raise HTTPException(status_code=400, detail="Maximum 10 files per batch")
    
    results = []
    
    for file in files:
        try:
            result = await upload_audio_file(file, db)
            results.append(result)
        except HTTPException as e:
            # Add error result for failed uploads
            results.append(UploadResponse(
                call_id=0,
                filename=file.filename or "unknown",
                original_filename=file.filename or "unknown",
                file_size=0,
                status="failed",
                message=f"Upload failed: {e.detail}"
            ))
    
    return results

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported audio formats."""
    return {
        "supported_formats": settings.SUPPORTED_AUDIO_FORMATS,
        "max_file_size": settings.MAX_CONTENT_LENGTH,
        "max_duration": settings.MAX_AUDIO_DURATION
    }

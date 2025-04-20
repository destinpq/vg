from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import time
import uuid

from ...db import crud, models
from ...db.database import get_db
from .. import schemas
from ...services.hunyuan_service import HunyuanService

router = APIRouter()
hunyuan_service = HunyuanService()

@router.get("/health", response_model=dict)
async def check_hunyuan_status():
    """Check the status of the Hunyuan API service"""
    try:
        health_status = hunyuan_service.check_health()
        return {
            "status": "ok" if health_status.get("status") == "healthy" else "error",
            "hunyuan_api": health_status,
            "server_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Hunyuan service unavailable: {str(e)}"
        )

@router.post("/generate", response_model=schemas.VideoStatus)
async def generate_hunyuan_video(
    video: schemas.VideoCreateHunyuan, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    creator_id: Optional[int] = None
):
    """Generate a video using Hunyuan model"""
    try:
        # Create video record in database
        db_video = crud.create_video(
            db=db,
            video=video,
            model_type="hunyuan",
            creator_id=creator_id
        )
        
        # Add the generation task to background tasks
        background_tasks.add_task(
            generate_video_task,
            db=db,
            video_id=db_video.video_id,
            prompt=video.prompt,
            width=video.width,
            height=video.height,
            num_inference_steps=video.num_inference_steps,
            output_format=video.output_format
        )
        
        # Return initial status
        video_url = f"/videos/{db_video.video_id}"
        return {
            "video_id": db_video.video_id,
            "status": "queued",
            "progress": 0.0,
            "message": "Video generation task has been queued",
            "video_url": video_url,
            "thumbnail_url": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating video: {str(e)}"
        )

@router.get("/status/{video_id}", response_model=schemas.VideoStatus)
async def get_hunyuan_video_status(video_id: str, db: Session = Depends(get_db)):
    """Get the status of a video generation task"""
    db_video = crud.get_video(db, video_id)
    
    if not db_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found"
        )
    
    # Determine progress based on status
    progress = 0.0
    if db_video.status == "queued":
        progress = 0.0
    elif db_video.status == "processing":
        progress = 50.0
    elif db_video.status == "completed":
        progress = 100.0
    
    # Generate URLs for video and thumbnail if available
    video_url = f"/videos/{video_id}" if db_video.file_path else None
    thumbnail_url = f"/thumbnails/{video_id}" if db_video.thumbnail_path else None
    
    return {
        "video_id": video_id,
        "status": db_video.status,
        "progress": progress,
        "message": f"Video generation is {db_video.status}",
        "video_url": video_url,
        "thumbnail_url": thumbnail_url
    }

@router.get("/videos", response_model=List[schemas.VideoResponse])
async def list_hunyuan_videos(
    skip: int = 0, 
    limit: int = 20,
    db: Session = Depends(get_db),
    creator_id: Optional[int] = None
):
    """List all Hunyuan videos"""
    videos = db.query(models.Video).filter(
        models.Video.model_type == "hunyuan"
    ).order_by(
        models.Video.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return videos

# Background task for video generation
async def generate_video_task(
    db: Session,
    video_id: str,
    prompt: str,
    width: int,
    height: int,
    num_inference_steps: int,
    output_format: str
):
    """Background task to generate video with Hunyuan"""
    try:
        # Update status to processing
        crud.update_video_status(db, video_id, "processing")
        
        # Generate video
        result = hunyuan_service.generate_video(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            height=height,
            width=width,
            output_format=output_format
        )
        
        if result["success"]:
            # Update video record with success info
            file_path = result["result"].get("local_video_path")
            
            # Update video metadata and status
            crud.update_video_metadata(
                db=db,
                video_id=video_id,
                width=width,
                height=height,
                parameters={
                    "num_inference_steps": num_inference_steps,
                    "output_format": output_format,
                    "prompt": prompt
                }
            )
            
            crud.update_video_status(
                db=db,
                video_id=video_id,
                status="completed",
                file_path=file_path
            )
        else:
            # Update status to failed
            crud.update_video_status(
                db=db,
                video_id=video_id,
                status="failed"
            )
            
    except Exception as e:
        # Update status to failed
        crud.update_video_status(
            db=db,
            video_id=video_id,
            status="failed"
        ) 
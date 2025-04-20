"""
Controller for Hunyuan video generation endpoints.
"""
import os
import time
import logging
from fastapi import APIRouter, HTTPException, Depends, status, Body, Query
from typing import Dict, Any

from ..services.hunyuan_service import hunyuan_service
from ..services.queue_service import video_queue
from ..schemas.hunyuan import (
    HunyuanGenerationRequest,
    HunyuanGenerationResponse,
    HunyuanStatusResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/status", response_model=HunyuanStatusResponse)
async def check_hunyuan_status():
    """Check the status of the Hunyuan API."""
    logger.info("Checking Hunyuan API status")
    
    # Check the status of the Hunyuan API
    health_status = await hunyuan_service.check_health()
    
    return {
        "status": "ok" if health_status.get("status") == "healthy" else "error",
        "hunyuan_api": health_status,
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@router.post("/generate", response_model=HunyuanGenerationResponse)
async def generate_hunyuan_video(request: HunyuanGenerationRequest):
    """Generate a video using the Hunyuan model on H100 GPU."""
    try:
        # Generate a unique ID for this request
        request_id = f"hunyuan_{int(time.time())}"
        
        # Set reasonable limits
        num_inference_steps = min(request.num_inference_steps, 100)
        height = min(request.height, 640)
        width = min(request.width, 1024)
        
        # Define the task to be executed
        async def generate_task():
            # Generate the video
            result = await hunyuan_service.generate_video(
                prompt=request.prompt,
                num_inference_steps=num_inference_steps,
                height=height,
                width=width,
                output_format=request.output_format
            )
            return result
        
        # Add the task to the queue
        task_id = await video_queue.add_task(
            generate_task,
            prompt=request.prompt,
            task_type="hunyuan",
            request_id=request_id
        )
        
        # Return the initial response
        return {
            "status": "pending",
            "request_id": request_id,
            "task_id": task_id,
            "message": "Video generation task added to queue",
            "prompt": request.prompt,
            "parameters": {
                "num_inference_steps": num_inference_steps,
                "height": height,
                "width": width,
                "output_format": request.output_format
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating Hunyuan video: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating video: {str(e)}"
        ) 
"""
DEPRECATED: Use app.controllers.hunyuan_controller instead.
This module remains for backward compatibility only.
"""
import os
import time
import logging
from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any
from pathlib import Path

from ..utils.config import get_settings
from ..services.video_queue import video_queue
from ...hunyuan_client import hunyuan_client

# Configure logging
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create router - FastAPI compatible
router = APIRouter()

@router.get("/status")
async def check_hunyuan_status():
    """Check the status of the Hunyuan API"""
    logger.info("Checking Hunyuan API status")
    
    # Check the status of the Hunyuan API
    health_status = hunyuan_client.check_health()
    
    return {
        "status": "ok" if health_status.get("status") == "healthy" else "error",
        "hunyuan_api": health_status,
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@router.post("/generate")
async def generate_hunyuan_video(request_data: Dict[str, Any] = Body(...)):
    """Generate a video using the Hunyuan model on H100 GPU"""
    try:
        # Get parameters from request
        prompt = request_data.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="No prompt provided")
        
        # Get optional parameters with defaults
        num_inference_steps = int(request_data.get("num_inference_steps", 50))
        height = int(request_data.get("height", 320))
        width = int(request_data.get("width", 576))
        output_format = request_data.get("output_format", "gif")
        
        # Set reasonable limits
        if num_inference_steps > 100:
            num_inference_steps = 100
        
        if height > 640:
            height = 640
        
        if width > 1024:
            width = 1024
        
        # Generate a unique ID for this request
        request_id = f"hunyuan_{int(time.time())}"
        
        # Add task to the queue
        async def generate_task():
            # Generate the video
            result = hunyuan_client.generate_video(
                prompt=prompt,
                num_inference_steps=num_inference_steps,
                height=height,
                width=width,
                output_format=output_format
            )
            
            # Return the result
            return result
        
        # Add the task to the queue
        task_id = await video_queue.add_task(
            generate_task,
            prompt=prompt,
            task_type="hunyuan",
            request_id=request_id
        )
        
        # Return the initial response
        return {
            "status": "pending",
            "request_id": request_id,
            "task_id": task_id,
            "message": "Video generation task added to queue",
            "prompt": prompt,
            "parameters": {
                "num_inference_steps": num_inference_steps,
                "height": height,
                "width": width,
                "output_format": output_format
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating Hunyuan video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
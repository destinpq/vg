"""
Hunyuan Video generation routes - Focused only on Tencent Hunyuan Video model
"""

import os
import json
import uuid
import time
import random
import logging
import asyncio
import subprocess
import re
import traceback
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Response
from pydantic import BaseModel, Field
from datetime import datetime

from app.utils.config import get_settings
from app.ai_core import HunyuanWrapper
from app.utils.gpu_info import get_gpu_info, get_gpu_acceleration_info
from app.services.video_queue import video_queue, VideoQueue, VideoStatus
from app.models.video import VideoGenerationRequest, VideoGenerationResponse, VideoGenerationStatus

# Initialize router
router = APIRouter()
settings = get_settings()

# Initialize the video generator
model = HunyuanWrapper()

@router.get("/health")
async def video_health_check():
    """
    Health check endpoint for the video generation service.
    """
    try:
        # Get GPU information
        gpu_info = get_gpu_info()
        acceleration_info = get_gpu_acceleration_info()
        
        return {
            "status": "healthy",
            "gpu_available": gpu_info["available"],
            "gpu_info": {
                "name": gpu_info.get("gpu_name", "Unknown"),
                "memory": f"{gpu_info.get('gpu_memory', 0):.1f} GB" if gpu_info["available"] else "N/A",
                "cuda_version": acceleration_info.get("cuda_version", "N/A")
            },
            "service": "Video Generation API"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "service": "Video Generation API"
        }

@router.get("/hunyuan-status")
async def hunyuan_status():
    """
    Get status of GPU and Hunyuan model
    """
    try:
        # Get GPU information
        gpu_info = get_gpu_info()
        acceleration_info = get_gpu_acceleration_info()
        
        # Build response
        return {
            "status": "GPU Detected" if gpu_info["available"] else "No GPU",
            "gpu_available": gpu_info["available"],
            "gpu_memory": f"{gpu_info['gpu_memory']:.2f} GB" if gpu_info["available"] else "N/A",
            "has_enough_memory": gpu_info.get("has_enough_memory", False),
            "cuda_available": acceleration_info["cuda_available"],
            "cuda_version": acceleration_info["cuda_version"],
            "system_info": acceleration_info["system_info"]
        }
    except Exception as e:
        # Return a graceful error response
        return {
            "status": "Error checking GPU",
            "gpu_available": False,
            "error": str(e),
            "gpu_memory": "N/A",
            "has_enough_memory": False
        }

@router.get("/hunyuan-video")
async def generate_hunyuan_video(
    prompt: str,
    width: int = 1280,
    height: int = 720,
    duration: int = 5,
    fps: int = 24,
    guidance_scale: float = 6.5,
    use_latest: bool = True,
    seed: Optional[int] = None,
    add_subtitles: bool = False,
    enable_lip_sync: bool = False,
    background_task: BackgroundTasks = BackgroundTasks()
):
    """
    Generate a video using the Hunyuan model directly on the server.
    
    Args:
        prompt: The text description of what to generate
        width: Video width (default: 1280)
        height: Video height (default: 720)
        duration: Video duration in seconds (default: 5)
        fps: Frames per second (default: 24)  
        guidance_scale: Guidance scale for generation (default: 6.5)
        use_latest: Whether to use the latest model version (default: True)
        seed: Optional random seed for reproducibility
        add_subtitles: Whether to add subtitles to the video
        enable_lip_sync: Whether to enable lip sync
        background_task: FastAPI background tasks
        
    Returns:
        Video generation response with job ID and status URL
    """
    # Create a unique job ID
    job_id = f"hunyuan_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    # Create output directory for this job
    output_dir = os.path.join(settings.OUTPUT_DIR, job_id)
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output path for the generated video
    output_filename = f"generated_video.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    # Function to update job status 
    async def update_status(job_id: str, status: str, progress: float = 0, message: str = ""):
        status_path = os.path.join(settings.OUTPUT_DIR, job_id, "status.json")
        data = {
            "job_id": job_id,
            "status": status,
            "progress": progress,
            "message": message,
            "updated_at": datetime.now().isoformat(),
        }
        
        # If processing is complete, add the output video URL
        if status == "completed":
            # Use a relative path that matches the static file mount point
            data["video_url"] = f"/output/{job_id}/{output_filename}"
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(status_path), exist_ok=True)
        
        # Write status to file
        with open(status_path, "w") as f:
            f.write(json.dumps(data))
    
    # Progress callback
    async def progress_callback(progress: float, message: str):
        await update_status(job_id, "processing", progress, message)
    
    # Generate subtitles if requested
    subtitles = None
    if add_subtitles:
        # Generate subtitles from the prompt
        subtitles = []
        
        # Simple subtitle generation from prompt (in a real app, this would be more sophisticated)
        sentences = re.split(r'[.!?]', prompt)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        total_duration = duration
        time_per_sentence = total_duration / len(sentences) if sentences else 0
        
        for i, sentence in enumerate(sentences):
            start_time = i * time_per_sentence
            end_time = (i + 1) * time_per_sentence
            
            subtitles.append({
                "text": sentence,
                "start": start_time,
                "end": end_time
            })
    
    # Function to run the generation in the background
    async def generate_in_background():
        try:
            # Update initial status
            await update_status(job_id, "processing", 0, "Initializing Hunyuan video generator...")
            
            # Use the HunyuanWrapper to generate the video
            try:
                # Create video request dictionary with all parameters
                video_request = {
                    "id": job_id,
                    "prompt": prompt,
                    "duration": duration,
                    "fps": fps,
                    "quality": "high",
                    "style": "realistic",
                    "subtitles": subtitles,
                    "enable_lip_sync": enable_lip_sync,
                    "subtitle_style": {
                        "font_size": 24,
                        "font_color": "white",
                        "background": True,
                        "background_color": "black",
                        "background_opacity": 0.5
                    }
                }
                
                # Generate the video using HunyuanWrapper
                result_path = await model.generate_video(
                    video_request=video_request,
                    progress_callback=progress_callback
                )
                
                # Update status to completed
                await update_status(job_id, "completed", 100, "Video generation completed")
            
            except Exception as e:
                logging.error(f"Error generating video: {str(e)}")
                await update_status(job_id, "failed", 0, f"Error generating video: {str(e)}")
            
        except Exception as e:
            logging.error(f"Error in video generation: {str(e)}")
            traceback.print_exc()
            await update_status(job_id, "failed", 0, f"Error: {str(e)}")
    
    # Add the generation task to the background
    background_task.add_task(generate_in_background)
    
    # Return immediate response with job ID
    return {
        "message": "Video generation started",
        "job_id": job_id,
        "status_url": f"/video/job-status/{job_id}",
        "expected_output": f"/output/{job_id}/{output_filename}",
        "parameters": {
            "prompt": prompt,
            "width": width,
            "height": height,
            "duration": duration,
            "fps": fps,
            "seed": seed,
            "use_latest": use_latest,
            "add_subtitles": add_subtitles,
            "enable_lip_sync": enable_lip_sync
        }
    }

@router.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of a video generation job
    
    Args:
        job_id: The ID of the job to check
        
    Returns:
        The current status of the job
    """
    # Construct the path to the status file
    status_path = os.path.join(settings.OUTPUT_DIR, job_id, "status.json")
    
    # Check if the status file exists
    if not os.path.exists(status_path):
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    try:
        # Read the status file
        with open(status_path, 'r') as f:
            status_data = json.loads(f.read())
            
        # If the video is completed, add the full URL to the video
        if status_data.get("status") == "completed" and "video_url" in status_data:
            base_url = f"{settings.VIDEO_BASE_URL}"
            rel_url = status_data["video_url"]
            if not rel_url.startswith("http"):
                status_data["video_url"] = f"{base_url}{rel_url}"
        
        return status_data
            
    except Exception as e:
        logging.error(f"Error reading job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reading job status: {str(e)}") 
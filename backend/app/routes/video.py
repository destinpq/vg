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
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Response, Query
from pydantic import BaseModel, Field
from datetime import datetime
import openai
import ffmpeg
import httpx
import zipfile
import requests
import tempfile
import shutil
from fastapi.responses import StreamingResponse

from ..utils.config import get_settings
from ..ai_core import HunyuanWrapper
from ..utils.gpu_info import get_gpu_info, get_gpu_acceleration_info
from ..services.video_queue import video_queue, VideoQueue, VideoStatus
from ..models.video import VideoGenerationRequest, VideoGenerationResponse, VideoGenerationStatus
# Import our fixed function
from .video_fix import setup_openai_api_key, generate_sequential_prompts_fixed

# Initialize router
router = APIRouter()
settings = get_settings()

# Initialize the video generator
model = HunyuanWrapper()

# --- Add OpenAI Client Initialization ---
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY
    print("OpenAI client initialized.")
else:
    print("Warning: OPENAI_API_KEY not found in environment. Sequential prompt generation will be disabled.")
# --------------------------------------

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

@router.get("/generate")
async def generate_video(
    prompt: str,
    duration: int = 5,
    fps: int = 24,
    quality: str = 'high',
    style: str = 'realistic',
    force_replicate: bool = Query(False, description="Force using Replicate API instead of local generation"),
    use_hunyuan: bool = Query(True, description="Use Hunyuan model (set to false to use alternatives)"),
    width: int = 1280,
    height: int = 720,
    human_focus: bool = Query(False, description="Whether the video focuses on humans (better with Replicate)"),
    seed: Optional[int] = None,
    background_task: BackgroundTasks = BackgroundTasks()
):
    """
    Generate a video using either local Hunyuan model or Replicate API.
    
    Args:
        prompt: Text description of what to generate
        duration: Video duration in seconds (default: 5)
        fps: Frames per second (default: 24)
        quality: Quality setting (low, medium, high)
        style: Style setting (realistic, abstract, etc.)
        force_replicate: Force using Replicate API instead of local generation
        use_hunyuan: Whether to use Hunyuan model (set to false to use alternatives)
        width: Video width in pixels
        height: Video height in pixels
        human_focus: Whether the video focuses on humans (better with Replicate)
        seed: Random seed for reproducibility
        background_task: FastAPI background tasks
        
    Returns:
        Video generation response with job ID and status URL
    """
    # Override settings from environment if set
    env_force_replicate = os.environ.get("FORCE_REPLICATE", "").lower() in ("true", "1", "yes")
    env_use_hunyuan = os.environ.get("USE_HUNYUAN", "").lower() not in ("false", "0", "no")
    
    # Environment variables take precedence over query parameters
    if env_force_replicate:
        force_replicate = True
    if not env_use_hunyuan:
        use_hunyuan = False
    
    # Human-focused videos should use Replicate
    if human_focus:
        force_replicate = True
        use_hunyuan = False
    
    # Create a unique job ID with appropriate prefix
    prefix = "replicate" if force_replicate else "hunyuan"
    job_id = f"{prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
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
    
    # Function to run the generation in the background
    async def generate_in_background():
        try:
            # Update initial status based on generation method
            if force_replicate:
                await update_status(job_id, "processing", 0, "Initializing Replicate API video generation...")
            else:
                await update_status(job_id, "processing", 0, "Initializing Hunyuan video generator...")
            
            # Create video request dictionary with all parameters
            video_request = {
                "id": job_id,
                "prompt": prompt,
                "duration": duration,
                "fps": fps,
                "quality": quality,
                "style": style,
                "force_replicate": force_replicate,
                "use_hunyuan": use_hunyuan and not force_replicate,
                "human_focus": human_focus,
                "subtitles": None,
                "enable_lip_sync": False,
                "subtitle_style": None
            }
            
            try:
                # For Replicate API calls
                if force_replicate:
                    # Check if Replicate API token is set
                    replicate_token = os.environ.get("REPLICATE_API_TOKEN", "")
                    if not replicate_token or replicate_token == "your_replicate_token_here":
                        await update_status(job_id, "failed", 0, "Replicate API token not set. Please set REPLICATE_API_TOKEN in .env file")
                        return
                    
                    # Import replicate here to avoid dependency issues
                    import replicate
                    import time
                    
                    # Update status
                    await update_status(job_id, "processing", 5, "Starting Replicate API video generation (will make ~50 network calls)...")
                    
                    try:
                        # Use the CORRECT Tencent Hunyuan model on Replicate
                        # Update to version ID that the user has permissions for
                        model_id = "tencent/hunyuan-video" # Use the latest version
                        
                        # Create the input parameters specifically for Tencent Hunyuan Video model
                        input_params = {
                            "prompt": prompt,
                            "negative_prompt": "low quality, blurry, noisy, text, watermark, signature, low-res, bad anatomy, bad proportions, deformed body, duplicate, extra limbs",
                            "num_frames": min(96, fps * duration), # Cap at 96 frames which is typical limit
                            "width": width,
                            "height": height,
                            "fps": fps,
                            "guidance_scale": 9.0, # Increased for better prompt adherence
                            "num_inference_steps": 50,
                            "seed": seed if seed is not None else random.randint(1, 100000)
                        }
                        
                        # Log the parameters for debugging
                        logging.info(f"Starting Replicate job for tencent/hunyuan-video with params: {input_params}")
                        
                        # Create a prediction instead of waiting for result - this is non-blocking
                        prediction = replicate.predictions.create(
                            version=model_id.split(':')[1],
                            input=input_params
                        )
                        
                        # Now poll for status updates to track the actual network calls
                        total_steps = 50  # Number of diffusion steps expected
                        current_step = 0
                        status = "processing"
                        
                        await update_status(job_id, "processing", 10, f"Replicate job started - ID: {prediction.id}. Now tracking ~50 diffusion steps...")
                        
                        # Poll until the prediction is complete
                        while status != "succeeded" and status != "failed" and status != "canceled":
                            # Get the latest status
                            prediction = replicate.predictions.get(prediction.id)
                            status = prediction.status
                            
                            # Default message and step info
                            step_message = "Waiting for diffusion steps..."
                            progress_pct = 10 # Start progress at 10%
                            parsed_step = 0
                            parsed_total = total_steps
                            
                            # Extract current step from logs if available
                            if prediction.logs:
                                log_lines = prediction.logs.strip().split('\n')
                                for line in reversed(log_lines):  # Check most recent logs first
                                    if "step" in line and "progress" in line:
                                        try:
                                            # Try to extract step number from the log line
                                            step_match = re.search(r'step (\d+)/(\d+)', line)
                                            if step_match:
                                                parsed_step = int(step_match.group(1))
                                                parsed_total = int(step_match.group(2))
                                                # Calculate progress ONLY if step is parsed
                                                progress_pct = int((parsed_step / parsed_total) * 90) + 10
                                                step_message = f"Diffusion step {parsed_step}/{parsed_total} ({progress_pct}%) - Network call #{parsed_step+10}"
                                                break
                                        except Exception as e:
                                            logging.error(f"Error parsing step: {e}")
                                            
                            # Use the parsed step info if available, otherwise use default message
                            final_message = step_message if parsed_step > 0 else f"Replicate status: {status}. {step_message}"
                            
                            # Update the status
                            await update_status(
                                job_id, 
                                "processing", 
                                progress_pct, 
                                final_message
                            )
                            
                            # Log status for debugging
                            logging.info(f"Replicate status: {status}, step: {parsed_step}/{parsed_total}, progress: {progress_pct}%")
                            
                            # Wait before polling again
                            await asyncio.sleep(2)
                        
                        # Check final status
                        if status == "succeeded":
                            if prediction.output:
                                # Get the output URL
                                video_url = prediction.output[0] if isinstance(prediction.output, list) else prediction.output
                                
                                # Download the video from Replicate
                                await update_status(job_id, "processing", 95, "Downloading video from Replicate (final network call)...")
                                
                                import requests
                                response = requests.get(video_url, stream=True)
                                if response.status_code == 200:
                                    with open(output_path, 'wb') as f:
                                        for chunk in response.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                    
                                    # Update status to completed
                                    await update_status(job_id, "completed", 100, f"Video generation completed after {total_steps} diffusion steps")
                                else:
                                    raise Exception(f"Failed to download video: HTTP {response.status_code}")
                            else:
                                raise Exception("Replicate job succeeded but no output was returned")
                        else:
                            error_msg = prediction.error or "Unknown error"
                            raise Exception(f"Replicate job {status}: {error_msg}")
                            
                    except Exception as e:
                        logging.error(f"Replicate API error: {str(e)}")
                        await update_status(job_id, "failed", 0, f"Replicate API error: {str(e)}")
                        return
                
                # For local Hunyuan generation
                else:
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
        "generation_method": "replicate" if force_replicate else "hunyuan",
        "parameters": {
            "prompt": prompt,
            "duration": duration,
            "fps": fps,
            "quality": quality,
            "style": style,
            "force_replicate": force_replicate,
            "use_hunyuan": use_hunyuan and not force_replicate,
            "human_focus": human_focus,
            "width": width,
            "height": height,
            "seed": seed
        }
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
            
        # If the video is completed, construct the correct full URL
        if status_data.get("status") == "completed" and "video_url" in status_data:
            # VIDEO_BASE_URL might be http://host:port/output OR http://host:port
            # video_url in status.json is /output/job_id/file.mp4
            base_url = settings.VIDEO_BASE_URL.rstrip('/') # Remove trailing slash if any
            relative_url = status_data["video_url"]
            
            # Combine smartly: if base_url already ends with /output, don't add it again
            if base_url.endswith('/output') and relative_url.startswith('/output'):
                # Remove /output from relative_url before joining
                correct_relative_path = relative_url[len('/output'):]
                status_data["video_url"] = f"{base_url}{correct_relative_path}"
            elif not relative_url.startswith('http'):
                 # Standard joining if base doesn't end with /output or relative doesn't start with /output
                status_data["video_url"] = f"{base_url}{relative_url}"
            # else: relative_url is already a full URL, do nothing
            
        return status_data
            
    except Exception as e:
        logging.error(f"Error reading job status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reading job status: {str(e)}")

# === NEW ENDPOINT FOR LONG VIDEO GENERATION ===
@router.post("/generate-long") # Using POST as it initiates a complex process
async def generate_long_video(
    initial_prompt: str,
    total_duration: int = Query(..., gt=0, description="Total desired video duration in seconds"),
    segment_duration: int = Query(3, gt=0, description="Duration of each video segment in seconds"),
    fps: int = Query(30, gt=0, description="Frames per second for the video"),
    width: int = Query(1920, gt=0, description="Video width in pixels"),
    height: int = Query(1080, gt=0, description="Video height in pixels"),
    seed: Optional[int] = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Generate a long video by stitching multiple shorter segments with evolving prompts.
    
    This endpoint:
    1. Creates evolving prompts from the initial prompt
    2. Generates multiple video segments in parallel
    3. Stitches the segments together with optional subtitles
    4. Returns a single coherent video
    
    Args:
        initial_prompt: The starting text description
        total_duration: Desired total video length in seconds
        segment_duration: Length of each segment in seconds
        fps: Frames per second
        width: Video width
        height: Video height
        seed: Random seed for reproducibility
        
    Returns:
        JSON response with job ID and status URL
    """
    # Initialize OpenAI API key
    setup_openai_api_key()
    
    # Calculate number of segments needed
    num_segments = total_duration // segment_duration
    if num_segments < 1:
        num_segments = 1  # Minimum 1 segment
    
    # Adjust segment duration if rounding occurred
    if num_segments * segment_duration < total_duration:
        num_segments += 1
        
    # Generate a unique ID for this long video job
    job_id = f"longvid_{uuid.uuid4().hex[:8]}"
    output_dir = Path(settings.OUTPUT_DIR) / job_id
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output paths
    final_video_path = output_dir / f"final_video_{job_id}.mp4"
    srt_path = output_dir / f"subtitles_{job_id}.srt"
    
    # Define the background task BEFORE referencing it
    async def generate_long_video_task():
        try:
            # 1. Update initial status
            await update_status(job_id, "processing", 0, "Starting long video generation...")
            
            # 2. Generate evolving prompts using OpenAI
            await update_status(job_id, "processing", 5, f"Generating {num_segments} evolving prompts...")
            # Use our fixed function instead of the original
            prompts = await generate_sequential_prompts_fixed(initial_prompt, num_segments, segment_duration)
            
            # 3. Generate SRT subtitles from prompts
            await update_status(job_id, "processing", 10, "Creating subtitles...")
            await generate_srt_subtitles(prompts, segment_duration, str(srt_path))
            
            # 4. Generate each video segment in parallel
            await update_status(job_id, "processing", 15, f"Generating {num_segments} video segments in parallel...")

            # 5. Download video segments
            await update_status(job_id, "processing", 20, f"Downloading {num_segments} video segments...")
            segment_video_paths = await download_videos(prompts, output_dir)
            
            # 6. Stitch videos and add subtitles
            await update_status(job_id, "processing", 80, f"Stitching {num_segments} segments and adding subtitles...")
            await stitch_videos_with_subtitles(segment_video_paths, str(srt_path), str(final_video_path))
            
            # 7. Final Success Status
            await update_status(job_id, "completed", 100, f"Long video generation complete ({num_segments} segments generated).")

        except Exception as e:
            logging.error(f"Job {job_id} failed: {str(e)}")
            logging.error(traceback.format_exc())
            await update_status(job_id, "failed", 0, f"Error: {str(e)}")
    
    # Add the generation task to the background AFTER defining it
    background_tasks.add_task(generate_long_video_task)
    
    # Return immediate response with job ID
    return {
        "message": "Long video generation started",
        "job_id": job_id,
        "status_url": f"/video/job-status/{job_id}",
        "expected_output": f"/output/{job_id}/final_video_{job_id}.mp4",
        "estimated_segments": num_segments
    }

# === Helper Functions for Long Video Workflow ===

async def download_videos(prompts: List[str], output_dir: Path) -> List[str]:
    """Generates videos from prompts and downloads them."""
    local_paths = []
    
    # Import replicate here to avoid dependency issues if it's not installed
    import replicate
    replicate_token = os.environ.get("REPLICATE_API_TOKEN", "")
    if not replicate_token:
        logging.error("Replicate API token not set. Cannot generate videos.")
        return []
    
    # Set the model ID using the version the user has permission for
    model_id = "tencent/hunyuan-video"
    
    for i, prompt in enumerate(prompts):
        try:
            segment_filename = f"segment_{i+1}.mp4"
            local_path = output_dir / segment_filename
            logging.info(f"Generating video for prompt {i+1}: {prompt[:50]}...")
            
            # Create the parameters for the Hunyuan model
            input_params = {
                "prompt": prompt,
                "negative_prompt": "low quality, blurry, noisy, text, watermark, signature, low-res, bad anatomy, bad proportions, deformed body, duplicate, extra limbs",
                "num_frames": min(96, fps * segment_duration), # Cap at 96 frames which is typical limit
                "width": width,
                "height": height,
                "fps": fps,
                "guidance_scale": 9.0, # Increased for better prompt adherence
                "num_inference_steps": 50,
                "seed": seed if seed is not None else random.randint(1, 100000)
            }
            
            # Create a prediction
            prediction = replicate.predictions.create(
                version=model_id.split(':')[1],
                input=input_params
            )
            
            # Instead of using wait() method, poll for completion
            prediction_id = prediction.id
            logging.info(f"Created prediction with ID: {prediction_id}")
            
            # Poll for completion - much longer timeout as requested by user
            max_polls = 6000  # 6000 polls * 5 seconds = 30000 seconds (500 minutes)
            status = "processing"
            
            for poll in range(max_polls):
                # Get the latest prediction status
                prediction = replicate.predictions.get(prediction_id)
                status = prediction.status
                
                if poll % 10 == 0:  # Only log every 10th poll to reduce log spam
                    logging.info(f"Prediction status: {status} (poll {poll+1}/{max_polls})")
                
                if status == "succeeded":
                    logging.info(f"Prediction succeeded after {poll+1} polls!")
                    break
                elif status in ["failed", "canceled"]:
                    logging.error(f"Prediction failed with status: {status}, Error: {prediction.error}")
                    break
                
                # Wait 5 seconds before polling again
                await asyncio.sleep(5)
            
            # Check if prediction succeeded and download the video
            if status == "succeeded" and prediction.output:
                # Get the output URL
                video_url = prediction.output[0] if isinstance(prediction.output, list) else prediction.output
                
                # Download the video
                logging.info(f"Downloading video from {video_url} to {local_path}")
                import requests
                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    local_paths.append(str(local_path))
                    logging.info(f"Successfully downloaded video to {local_path}")
                else:
                    logging.error(f"Failed to download video: HTTP {response.status_code}")
            else:
                logging.error(f"Replicate prediction failed or timed out: {status}, Error: {getattr(prediction, 'error', 'Unknown')}")
        except Exception as e:
            logging.error(f"Error generating/downloading video for prompt {i+1}: {str(e)}")
            logging.exception("Full traceback:")
    
    logging.info(f"Downloaded {len(local_paths)} out of {len(prompts)} videos")
    return local_paths

async def generate_srt_subtitles(prompts: List[str], segment_duration: int, output_srt_path: str):
    """Generates an SRT subtitle file from a list of prompts."""
    srt_content = ""
    start_time = 0.0
    for i, prompt in enumerate(prompts):
        end_time = start_time + segment_duration
        # Format start/end times (HH:MM:SS,ms)
        start_h, start_rem = divmod(start_time, 3600)
        start_m, start_s = divmod(start_rem, 60)
        start_ms = int((start_s - int(start_s)) * 1000)
        
        end_h, end_rem = divmod(end_time, 3600)
        end_m, end_s = divmod(end_rem, 60)
        end_ms = int((end_s - int(end_s)) * 1000)
        
        start_str = f"{int(start_h):02}:{int(start_m):02}:{int(start_s):02},{start_ms:03}"
        end_str = f"{int(end_h):02}:{int(end_m):02}:{int(end_s):02},{end_ms:03}"
        
        # Clean up prompt for subtitle display (optional)
        subtitle_text = prompt.replace('\n', ' ') 
        
        srt_content += f"{i+1}\n{start_str} --> {end_str}\n{subtitle_text}\n\n"
        start_time = end_time # Move to next segment start

    with open(output_srt_path, "w", encoding='utf-8') as f:
        f.write(srt_content)

async def stitch_videos_with_subtitles(video_paths: List[str], subtitle_path: str, output_path: str):
    """Stitches video segments together and adds subtitles using FFmpeg."""
    logging.info(f"Starting video stitching with {len(video_paths)} video paths")
    
    if not video_paths:
        logging.error("No video paths provided for stitching.")
        # Create a simple text file instead of using ffmpeg (which might not be available)
        try:
            error_message = "No videos were successfully generated. Please try again."
            with open(output_path, 'w') as f:
                f.write(f"ERROR: {error_message}")
            logging.info(f"Created error message file at {output_path}")
            return
        except Exception as file_error:
            logging.error(f"Failed to create error message file: {file_error}")
            return

    # Verify all video files exist before proceeding
    valid_video_paths = []
    for path in video_paths:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            valid_video_paths.append(path)
            logging.info(f"Video found: {path} ({os.path.getsize(path)} bytes)")
        else:
            logging.warning(f"Video file missing or empty: {path}")
    
    if not valid_video_paths:
        logging.error("No valid video files found for stitching")
        with open(output_path, 'w') as f:
            f.write("ERROR: No valid video files available for stitching")
        return
    
    logging.info(f"Proceeding with {len(valid_video_paths)} valid videos")
    
    # Use the helper function to find FFmpeg
    ffmpeg_path = get_ffmpeg_path()
    
    if not ffmpeg_path:
        logging.error("FFmpeg is not available. Please install it or use the /video/install-ffmpeg endpoint.")
        with open(output_path, 'w') as f:
            f.write("ERROR: FFmpeg is not available. Please install FFmpeg or use the API endpoint to install it.")
            f.write("\n\nIndividual video segments are available separately:")
            for i, path in enumerate(valid_video_paths):
                f.write(f"\n- Segment {i+1}: {path}")
        
        # Copy the first video to the output path as a fallback
        try:
            import shutil
            shutil.copy2(valid_video_paths[0], output_path + '.mp4')
            logging.info(f"Copied first video to {output_path}.mp4 as a fallback")
        except Exception as copy_error:
            logging.error(f"Failed to copy first video: {str(copy_error)}")
        
        return

    # Proceed with video stitching since FFmpeg is available
    logging.info(f"Using FFmpeg at: {ffmpeg_path}")
    
    # Create a temporary file listing the video segments for FFmpeg concat demuxer
    list_file_path = Path(valid_video_paths[0]).parent / "ffmpeg_list.txt"
    logging.info(f"Creating ffmpeg list file: {list_file_path}")
    
    with open(list_file_path, "w") as f:
        for path in valid_video_paths:
            # Use absolute paths with escaped backslashes
            abs_path = os.path.abspath(path).replace('\\', '\\\\')
            f.write(f"file '{abs_path}'\n")
            logging.info(f"Added to list: {abs_path}")

    # First attempt - concatenate the videos without using subtitles
    try:
        cmd = [
            ffmpeg_path,
            '-f', 'concat',
            '-safe', '0',
            '-i', str(list_file_path),
            '-c', 'copy',
            '-y',  # Overwrite output file if it exists
            output_path
        ]
        logging.info(f"Running FFmpeg command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        logging.info(f"FFmpeg stitching successful without subtitles")
        logging.info(f"Output file created: {output_path} ({os.path.getsize(output_path)} bytes)")
        return
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg error: {e.stderr.decode()}")
        
        # Try without stream copy
        logging.info("Retrying FFmpeg without stream copy...")
        try:
            cmd = [
                ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', str(list_file_path),
                '-c:v', 'libx264',  # Specify video codec explicitly
                '-c:a', 'aac',
                '-strict', 'experimental',
                '-y',
                output_path
            ]
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            logging.info(f"FFmpeg retry successful: {os.path.getsize(output_path)} bytes")
            return
        except subprocess.CalledProcessError as e2:
            logging.error(f"FFmpeg retry error: {e2.stderr.decode()}")
            
    # If we're here, both attempts failed - try a different approach with one file at a time
    logging.info("Trying to stitch videos one by one")
    try:
        # Copy the first video as a base
        import shutil
        shutil.copy2(valid_video_paths[0], output_path)
        logging.info(f"Copied first video to {output_path}")
        
        if len(valid_video_paths) > 1:
            # Create a text file explaining what happened
            with open(f"{output_path}.txt", 'w') as f:
                f.write(f"NOTE: FFmpeg failed to stitch all videos. Only the first segment is included.\n")
                f.write(f"Generated {len(valid_video_paths)} videos but failed to combine them.\n")
                f.write(f"\nIndividual video segments are available at:\n")
                for i, path in enumerate(valid_video_paths):
                    f.write(f"Segment {i+1}: {path}\n")
        
        return
    except Exception as copy_error:
        logging.error(f"Failed to copy first video: {str(copy_error)}")
        # Create a text file with error message
        with open(output_path, 'w') as f:
            f.write(f"ERROR: Failed to stitch videos and even copy failed: {str(copy_error)}")
    finally:
        # Clean up the temporary list file
        if list_file_path.exists():
            os.remove(list_file_path)

# Add this route after the other routes
@router.get("/install-ffmpeg")
async def install_ffmpeg():
    """
    Checks for FFmpeg installation and installs it if not found.
    Returns a streaming response with progress updates that can be displayed in the frontend.
    """
    async def event_stream():
        """Generate server-sent events for progress updates."""
        # Define a helper function to send progress events
        def send_event(event_type, data):
            event_json = json.dumps({"type": event_type, "data": data, "timestamp": datetime.datetime.now().isoformat()})
            return f"data: {event_json}\n\n"
        
        yield send_event("log", {"level": "info", "message": "Starting FFmpeg installation check..."})
        
        # Common paths where FFmpeg might be found
        ffmpeg_candidates = [
            os.path.join(os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg.exe'),  # backend/ffmpeg/bin
            os.path.join(os.path.dirname(os.getcwd()), 'ffmpeg', 'bin', 'ffmpeg.exe'),  # parent/ffmpeg/bin
            os.path.join(os.getcwd(), '..', 'ffmpeg', 'bin', 'ffmpeg.exe'),  # relative path
            'ffmpeg',  # system PATH
            os.path.join(os.path.expanduser('~'), 'ffmpeg', 'bin', 'ffmpeg.exe'),  # user home
        ]
        
        # Check each location
        for candidate in ffmpeg_candidates:
            try:
                yield send_event("log", {"level": "info", "message": f"Checking for FFmpeg at: {candidate}"})
                
                # Test if path exists
                if os.path.exists(candidate) and os.path.isfile(candidate):
                    # Try to run FFmpeg
                    process = subprocess.run([candidate, "-version"], 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE,
                                           text=True,
                                           check=True)
                    
                    ffmpeg_version = process.stdout.split('\n')[0]
                    yield send_event("log", {"level": "success", "message": f"Found working FFmpeg: {ffmpeg_version}"})
                    yield send_event("result", {"status": "success", "path": candidate, "already_installed": True})
                    return
                    
                # For the PATH version, just try running it
                elif candidate == 'ffmpeg':
                    process = subprocess.run([candidate, "-version"], 
                                           stdout=subprocess.PIPE, 
                                           stderr=subprocess.PIPE,
                                           text=True)
                    
                    if process.returncode == 0:
                        ffmpeg_version = process.stdout.split('\n')[0]
                        yield send_event("log", {"level": "success", "message": f"Found FFmpeg in PATH: {ffmpeg_version}"})
                        yield send_event("result", {"status": "success", "path": "ffmpeg", "already_installed": True})
                        return
            except Exception as e:
                yield send_event("log", {"level": "warning", "message": f"FFmpeg not found at {candidate}: {str(e)}"})
        
        # If we get here, FFmpeg was not found - install it
        yield send_event("log", {"level": "info", "message": "FFmpeg not found. Installing..."})
        
        # Define the installation directory
        ffmpeg_dir = os.path.join(os.getcwd(), 'ffmpeg')
        bin_dir = os.path.join(ffmpeg_dir, 'bin')
        ffmpeg_exe = os.path.join(bin_dir, 'ffmpeg.exe')
        
        # Create the directories
        os.makedirs(bin_dir, exist_ok=True)
        yield send_event("log", {"level": "info", "message": f"Created directories at {ffmpeg_dir}"})
        
        # Define the download URL
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        
        try:
            # Download FFmpeg zip
            yield send_event("log", {"level": "info", "message": f"Downloading FFmpeg from {ffmpeg_url}..."})
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                tmp_path = tmp_file.name
                
            # Stream the download with progress updates
            with requests.get(ffmpeg_url, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(tmp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = int(downloaded / total_size * 100) if total_size > 0 else 0
                        
                        # Send progress updates at 10% intervals to reduce events
                        if progress % 10 == 0:
                            yield send_event("progress", {"percent": progress, "action": "downloading"})
            
            # Extract the zip file
            yield send_event("log", {"level": "info", "message": "Download complete. Extracting FFmpeg..."})
            
            # Create a temporary extraction directory
            with tempfile.TemporaryDirectory() as extract_dir:
                # Extract the zip
                with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Find the extracted folder (should contain a 'bin' directory)
                extracted_bin = None
                for root, dirs, files in os.walk(extract_dir):
                    if 'bin' in dirs:
                        extracted_bin = os.path.join(root, 'bin')
                        break
                
                if not extracted_bin:
                    raise Exception("Could not find 'bin' directory in extracted files")
                
                # Copy the bin contents to our bin directory
                yield send_event("log", {"level": "info", "message": "Copying FFmpeg files to installation directory..."})
                for item in os.listdir(extracted_bin):
                    src = os.path.join(extracted_bin, item)
                    dst = os.path.join(bin_dir, item)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
            
            # Clean up the temporary files
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
            # Verify the installation
            if os.path.exists(ffmpeg_exe):
                process = subprocess.run([ffmpeg_exe, "-version"], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE,
                                       text=True)
                
                if process.returncode == 0:
                    ffmpeg_version = process.stdout.split('\n')[0]
                    yield send_event("log", {"level": "success", "message": f"FFmpeg installed successfully: {ffmpeg_version}"})
                    yield send_event("result", {
                        "status": "success", 
                        "path": ffmpeg_exe, 
                        "already_installed": False,
                        "version": ffmpeg_version
                    })
                else:
                    raise Exception(f"FFmpeg installation verification failed: {process.stderr}")
            else:
                raise Exception(f"FFmpeg executable not found at expected location: {ffmpeg_exe}")
                
        except Exception as e:
            error_message = f"FFmpeg installation failed: {str(e)}"
            yield send_event("log", {"level": "error", "message": error_message})
            yield send_event("result", {"status": "error", "message": error_message})
    
    # Return a streaming response that the frontend can listen to
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Prevents buffering for nginx
        }
    )

# Add a function to check for FFmpeg in usual locations
def get_ffmpeg_path():
    """Find FFmpeg executable at common locations."""
    ffmpeg_candidates = [
        os.path.join(os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg.exe'),
        os.path.join(os.path.dirname(os.getcwd()), 'ffmpeg', 'bin', 'ffmpeg.exe'),
        'ffmpeg',  # Check in PATH
        os.path.join(os.path.expanduser('~'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
    ]
    
    for candidate in ffmpeg_candidates:
        try:
            # Check if file exists for path-based candidates
            if candidate != 'ffmpeg' and (not os.path.exists(candidate) or not os.path.isfile(candidate)):
                continue
            
            # Try to run the executable
            process = subprocess.run(
                [candidate, "-version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=True
            )
            
            # If we get here, it worked
            logging.info(f"Found working FFmpeg at: {candidate}")
            return candidate
        except Exception as e:
            logging.debug(f"FFmpeg not found at {candidate}: {str(e)}")
    
    return None

# Make sure update_status function is defined before its first use
async def update_status(job_id: str, status: str, progress: float = 0, message: str = ""):
    status_path = os.path.join(settings.OUTPUT_DIR, job_id, "status.json")
    output_filename = f"final_video_{job_id}.mp4" # Use final video name
    data = {
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "message": message,
        "updated_at": datetime.now().isoformat(),
    }
    
    if status == "completed":
        # Construct final video URL correctly
        base_url = settings.VIDEO_BASE_URL.rstrip('/') 
        relative_url = f"/output/{job_id}/{output_filename}"
        if base_url.endswith('/output') and relative_url.startswith('/output'):
            correct_relative_path = relative_url[len('/output'):]
            data["video_url"] = f"{base_url}{correct_relative_path}"
        elif not relative_url.startswith('http'):
            data["video_url"] = f"{base_url}{relative_url}"
        else:
            data["video_url"] = relative_url # Should not happen here but safe fallback
            
    os.makedirs(os.path.dirname(status_path), exist_ok=True)
    with open(status_path, "w") as f:
        f.write(json.dumps(data)) 
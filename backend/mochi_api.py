"""
DEPRECATED: Mochi API wrapper.
This module forwards to app.controllers.mochi_controller for MVC structure.
"""
import os
import uuid
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Load configuration
MODEL_DIR = os.getenv("MOCHI_MODEL_DIR", "models/weights")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5001")
USE_FALLBACK = os.getenv("USE_FALLBACK", "1").lower() in ("1", "true")

# Create FastAPI app
app = FastAPI(
    title="Mochi-1 Video Generation API",
    description="API for generating videos using Mochi-1 model",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the output directory if it doesn't exist
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

# Mount static files (for accessing generated videos)
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")

# Store job information
JOBS = {}

@app.post("/generate")
async def generate_video(request_data: Dict[str, Any] = Body(...), background_tasks: BackgroundTasks = None):
    """
    DEPRECATED: Generate a video based on the provided prompt.
    Use the new controller in app.controllers.video_controller instead.
    
    This is a simplified compatibility version that always returns a placeholder.
    """
    # Generate a unique ID for this video
    video_id = str(uuid.uuid4())
    
    # Get prompt from request
    prompt = request_data.get("prompt", "A placeholder video")
    
    # Set status to completed immediately for backward compatibility
    JOBS[video_id] = {
        "video_id": video_id,
        "status": "completed",
        "prompt": prompt,
        "video_url": f"{BASE_URL}/outputs/video_{video_id}.mp4",
        "fallback": True,
        "message": "Using simplified fallback mode. Please use the new API."
    }
    
    # Return the response immediately
    return {
        "video_id": video_id,
        "prompt": prompt,
        "video_url": f"{BASE_URL}/outputs/video_{video_id}.mp4",
        "status": "completed",
        "message": "Using simplified fallback mode. Please use the new API."
    }

@app.get("/status/{video_id}")
async def get_video_status(video_id: str):
    """
    DEPRECATED: Get the status of a video generation job.
    Use the new controller in app.controllers.video_controller instead.
    """
    if video_id not in JOBS:
        raise HTTPException(status_code=404, detail="Video job not found")
    
    return JOBS[video_id]

@app.get("/")
async def root():
    return {
        "message": "DEPRECATED: Mochi-1 Video Generation API",
        "docs": "Please use the new API at /docs",
        "fallback_mode": True
    }

if __name__ == "__main__":
    """This direct execution is kept for backward compatibility."""
    uvicorn.run("mochi_api:app", host="0.0.0.0", port=5001, reload=True) 
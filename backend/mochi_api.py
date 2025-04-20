import os
import uuid
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Union
import time
import base64

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import tempfile

# Create the output directory if it doesn't exist
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

# Configuration
MODEL_DIR = os.getenv("MOCHI_MODEL_DIR", "models/weights")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5001")
USE_FALLBACK = os.getenv("USE_FALLBACK", "0").lower() in ("1", "true")

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

# Mount static files (for accessing generated videos)
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")

# Request models
class VideoRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    width: Optional[int] = 848
    height: Optional[int] = 480
    num_frames: Optional[int] = 31
    seed: Optional[int] = None
    cfg_scale: Optional[float] = 6.0
    num_steps: Optional[int] = 64

class VideoResponse(BaseModel):
    video_id: str
    prompt: str
    video_url: str
    status: str = "completed"

class StatusResponse(BaseModel):
    video_id: str
    status: str
    prompt: str
    video_url: Optional[str] = None
    error: Optional[str] = None

# Store job information
JOBS = {}

# Generate a random seed if not provided
def get_random_seed():
    import random
    return random.randint(1, 2147483647)

# Fallback function to generate a placeholder video
def generate_placeholder_video(prompt: str, output_path: Path) -> Path:
    """
    Generate a placeholder video with text for testing purposes
    """
    try:
        import cv2
        import numpy as np
        
        # Create a simple text video (5 seconds at 24fps)
        width, height = 640, 360
        fps = 24
        duration = 5  # seconds
        
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # Generate frames
        for i in range(duration * fps):
            # Create a frame with gradient background
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add a gradient background
            for y in range(height):
                for x in range(width):
                    frame[y, x] = [
                        int(100 + 50 * np.sin(i / (fps * 2) + x / 100)),
                        int(100 + 50 * np.cos(i / (fps * 2) + y / 100)),
                        int(150 + 50 * np.sin(i / (fps * 2) + (x+y) / 200))
                    ]
            
            # Add text
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            # Add prompt text
            lines = []
            words = prompt.split()
            current_line = ""
            for word in words:
                if len(current_line + " " + word) > 40:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line += " " + word if current_line else word
            if current_line:
                lines.append(current_line)
            
            y_pos = height // 3
            for line in lines:
                text_size = cv2.getTextSize(line, font, 0.7, 2)[0]
                x_pos = (width - text_size[0]) // 2
                
                # Add text shadow for better readability
                cv2.putText(
                    frame, line, (x_pos + 2, y_pos + 2),
                    font, 0.7, (0, 0, 0), 2
                )
                cv2.putText(
                    frame, line, (x_pos, y_pos),
                    font, 0.7, (255, 255, 255), 2
                )
                y_pos += 30
            
            # Add frame count and "PLACEHOLDER" text
            cv2.putText(
                frame, f"Frame: {i}/{fps*duration}", (10, height-40),
                font, 0.5, (255, 255, 255), 1
            )
            cv2.putText(
                frame, "PLACEHOLDER (Mochi-1 not available)", (10, height-15),
                font, 0.5, (255, 255, 255), 1
            )
            
            video.write(frame)
        
        video.release()
        
        # Save metadata for reference
        metadata = {
            "prompt": prompt,
            "fallback": True,
            "timestamp": time.time(),
            "fps": fps,
            "duration": duration
        }
        with open(output_path.with_suffix('.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return output_path
        
    except Exception as e:
        print(f"Error in fallback video generation: {e}")
        raise

# Function to execute the CLI command
def run_mochi_cli(
    video_id: str,
    prompt: str,
    negative_prompt: str = "",
    width: int = 848,
    height: int = 480,
    num_frames: int = 31,
    seed: Optional[int] = None,
    cfg_scale: float = 6.0,
    num_steps: int = 64
) -> None:
    try:
        # Set a random seed if not provided
        if seed is None:
            seed = get_random_seed()
            
        # Create output path
        output_path = OUTPUTS_DIR / f"video_{video_id}.mp4"
        
        # Check if we should use fallback mode
        cli_script_path = Path("models/demos/cli.py")
        if USE_FALLBACK or not cli_script_path.exists():
            print(f"Using fallback video generator. Mochi CLI not found or fallback mode enabled.")
            generate_placeholder_video(prompt, output_path)
            
            # Update job status
            JOBS[video_id] = {
                "video_id": video_id,
                "status": "completed",
                "prompt": prompt,
                "video_url": f"{BASE_URL}/outputs/video_{video_id}.mp4",
                "fallback": True
            }
            return
        
        # Build command
        cmd = [
            "python", str(cli_script_path),
            "--prompt", prompt,
            "--negative_prompt", negative_prompt,
            "--width", str(width),
            "--height", str(height),
            "--num_frames", str(num_frames),
            "--seed", str(seed),
            "--cfg_scale", str(cfg_scale),
            "--num_steps", str(num_steps),
            "--model_dir", MODEL_DIR,
            "--out_dir", str(OUTPUTS_DIR)
        ]
        
        # Run the command
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the output to find the generated video path
        output_lines = process.stdout.splitlines()
        generated_path = None
        for line in output_lines:
            if "Video generated at:" in line:
                generated_path = line.split("Video generated at:")[-1].strip()
                break
        
        if not generated_path:
            raise Exception("Could not find generated video path in output")
        
        # Rename the generated file to match our naming convention
        generated_path = Path(generated_path)
        if output_path != generated_path and generated_path.exists():
            os.rename(generated_path, output_path)
            
            # Also rename the JSON metadata if it exists
            json_path = generated_path.with_suffix('.json')
            if json_path.exists():
                os.rename(json_path, output_path.with_suffix('.json'))
        
        # Update job status
        JOBS[video_id] = {
            "video_id": video_id,
            "status": "completed",
            "prompt": prompt,
            "video_url": f"{BASE_URL}/outputs/video_{video_id}.mp4"
        }
        
    except Exception as e:
        try:
            # Try to generate a fallback video on error
            print(f"Error running Mochi CLI: {e}")
            print("Attempting to generate fallback video")
            output_path = OUTPUTS_DIR / f"video_{video_id}.mp4"
            generate_placeholder_video(prompt, output_path)
            
            # Update job status
            JOBS[video_id] = {
                "video_id": video_id,
                "status": "completed",
                "prompt": prompt,
                "video_url": f"{BASE_URL}/outputs/video_{video_id}.mp4",
                "fallback": True,
                "original_error": str(e)
            }
        except Exception as fallback_error:
            # Update job with error if fallback also fails
            JOBS[video_id] = {
                "video_id": video_id,
                "status": "failed",
                "prompt": prompt,
                "error": f"Original error: {str(e)}. Fallback error: {str(fallback_error)}"
            }
            print(f"Error generating fallback video: {fallback_error}")

@app.post("/generate", response_model=VideoResponse)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Generate a video based on the provided prompt
    
    This endpoint runs Mochi-1 CLI in the background and returns a unique ID.
    You can check the status using the /status/{video_id} endpoint.
    """
    # Generate a unique ID for this video
    video_id = str(uuid.uuid4())
    
    # Store initial job info
    JOBS[video_id] = {
        "video_id": video_id,
        "status": "processing",
        "prompt": request.prompt
    }
    
    # Start video generation in the background
    background_tasks.add_task(
        run_mochi_cli,
        video_id=video_id,
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        width=request.width,
        height=request.height,
        num_frames=request.num_frames,
        seed=request.seed,
        cfg_scale=request.cfg_scale,
        num_steps=request.num_steps
    )
    
    # Return the response immediately
    return {
        "video_id": video_id,
        "prompt": request.prompt,
        "video_url": f"{BASE_URL}/outputs/video_{video_id}.mp4",
        "status": "processing"
    }

@app.get("/status/{video_id}", response_model=StatusResponse)
async def get_video_status(video_id: str):
    """
    Get the status of a video generation job
    """
    if video_id not in JOBS:
        raise HTTPException(status_code=404, detail="Video job not found")
    
    return JOBS[video_id]

@app.get("/")
async def root():
    return {
        "message": "Mochi-1 Video Generation API",
        "endpoints": {
            "generate": "/generate - POST request with prompt information",
            "status": "/status/{video_id} - GET the status of a video generation job"
        },
        "fallback_mode": USE_FALLBACK
    }

if __name__ == "__main__":
    uvicorn.run("mochi_api:app", host="0.0.0.0", port=5001, reload=True) 
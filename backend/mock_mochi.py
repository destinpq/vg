import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import cv2
import numpy as np
import tempfile
import os
from pathlib import Path

app = FastAPI(title="Mock Mochi-1 Service")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    prompt: str

class VideoResponse(BaseModel):
    video_data: str
    prompt: str

@app.post("/generate", response_model=VideoResponse)
async def generate_video(request: VideoRequest):
    """
    Mock endpoint for video generation.
    Creates a simple video with the prompt text.
    """
    prompt = request.prompt
    
    # Create a simple text video (3 seconds at 24fps)
    width, height = 640, 360
    fps = 24
    duration = 3
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a temporary video file
        video_path = Path(temp_dir) / "temp_video.mp4"
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))
        
        # Generate frames
        for i in range(fps * duration):
            # Create a frame with gradient background
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add a gradient background
            for y in range(height):
                for x in range(width):
                    # Create color gradient based on position and time
                    frame[y, x] = [
                        int(100 + 50 * np.sin(i / (fps * 2) + x / 100)),
                        int(100 + 50 * np.cos(i / (fps * 2) + y / 100)),
                        int(150 + 50 * np.sin(i / (fps * 2) + (x+y) / 200))
                    ]
            
            # Add text
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = f"Prompt: {prompt}"
            # Simple text wrapping by truncating
            if len(text) > 40:
                text = text[:37] + "..."
            
            text_size = cv2.getTextSize(text, font, 0.7, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = height // 2
            
            # Add outline for better visibility
            cv2.putText(frame, text, (text_x+2, text_y+2), 
                        font, 0.7, (0, 0, 0), 2)
            cv2.putText(frame, text, (text_x, text_y), 
                        font, 0.7, (255, 255, 255), 2)
            
            # Add frame count
            cv2.putText(frame, f"Frame: {i}/{fps*duration}", (10, height-20), 
                        font, 0.5, (255, 255, 255), 1)
            
            video.write(frame)
        
        video.release()
        
        # Read the video file as bytes
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        
        # Encode to base64
        video_base64 = base64.b64encode(video_bytes).decode("utf-8")
        
        return {"video_data": video_base64, "prompt": prompt}

@app.get("/")
def read_root():
    return {
        "message": "Mock Mochi-1 Video Generation Service",
        "endpoints": {
            "generate": "/generate - POST request with {prompt: string}"
        }
    }

if __name__ == "__main__":
    uvicorn.run("mock_mochi:app", host="0.0.0.0", port=5001, reload=True) 
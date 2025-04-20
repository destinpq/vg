import os
import sys
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Any
from app.utils.config import get_settings
from app.services.video_queue import video_queue

# Get settings
settings = get_settings()

class VideoService:
    """
    Service for handling video generation
    """
    def __init__(self):
        # Use settings for configuration
        self.output_dir = Path(settings.OUTPUT_DIR)
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory: {self.output_dir}")
        
        # URL for video access
        self.base_url = settings.VIDEO_BASE_URL
        print(f"Video base URL: {self.base_url}")
        
    async def generate_video(self, prompt: str, duration: float = 5.0, fps: int = 24) -> Dict[str, Any]:
        """
        Generate a video based on the provided prompt
        This is kept for backward compatibility
        """
        # Create unique ID for this video
        video_id = str(uuid.uuid4())
        # Use resolve() to get absolute path
        output_path = (self.output_dir / f"{video_id}.mp4").resolve()
        
        # Add job to queue
        from app.models.video import VideoGenerationRequest
        request = VideoGenerationRequest(prompt=prompt, duration=duration, fps=fps)
        await video_queue.add_job(video_id, request, output_path)
        
        # Return response with job information
        video_url = f"{self.base_url}/{video_id}.mp4"
        print(f"Video URL returned to client: {video_url}")
        
        return {
            "video_id": video_id,
            "video_url": video_url,
            "prompt": prompt,
            "status": "processing"
        }
            
    async def get_job_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get the status of a video generation job from the queue
        """
        return await video_queue.get_job_status(video_id) 
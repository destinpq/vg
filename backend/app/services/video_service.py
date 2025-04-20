"""
Video generation service.
"""
import os
import time
import logging
import asyncio
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..models.video import Video
from ..schemas.video import VideoGenerationRequest
from ..config.settings import settings
from .database_service import DatabaseService

# Configure logging
logger = logging.getLogger(__name__)

class VideoService:
    """Service for video generation and management."""
    
    def __init__(self, db: DatabaseService):
        """Initialize the service with database connection."""
        self.db = db
        self.output_dir = Path(settings.OUTPUT_DIR)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def create_video_request(self, request: VideoGenerationRequest) -> Video:
        """Create a new video generation request and store it in the database."""
        # Generate a unique ID for this request
        video_id = f"video_{int(time.time())}"
        
        # Create a directory for this video
        video_dir = self.output_dir / video_id
        os.makedirs(video_dir, exist_ok=True)
        
        # Create a new video record
        video = Video(
            id=video_id,
            prompt=request.prompt,
            status="pending",
            width=request.width,
            height=request.height,
            fps=request.fps,
            num_inference_steps=request.num_inference_steps,
            metadata={
                "style": request.style,
                "quality": request.quality,
                "duration": request.duration,
                "enable_lip_sync": request.enable_lip_sync,
            }
        )
        
        # Save to database
        self.db.add(video)
        await self.db.commit()
        
        logger.info(f"Created video generation request with ID: {video_id}")
        return video
    
    async def get_video_status(self, video_id: str) -> Optional[Video]:
        """Get the status of a video generation request."""
        video = await self.db.get(Video, video_id)
        return video
    
    async def update_video_status(self, video_id: str, status: str, **kwargs) -> Optional[Video]:
        """Update the status of a video generation request."""
        video = await self.db.get(Video, video_id)
        if not video:
            return None
        
        video.status = status
        
        # Update other properties if provided
        for key, value in kwargs.items():
            if hasattr(video, key):
                setattr(video, key, value)
        
        await self.db.commit()
        logger.info(f"Updated video {video_id} status to {status}")
        return video
    
    def stitch_videos(self, video_paths: List[str], output_path: str) -> str:
        """
        Stitch multiple videos together using ffmpeg.
        
        This function concatenates videos with the same resolution and frame rate.
        It uses a concat demuxer through an intermediate file list.
        
        Args:
            video_paths: List of paths to video files to stitch together
            output_path: Path where the stitched video will be saved
        
        Returns:
            Path to the stitched video file
        
        Raises:
            ValueError: If the video list is empty or if videos have different resolutions/frame rates
            subprocess.CalledProcessError: If ffmpeg command fails
            OSError: If file operations fail
        """
        if not video_paths:
            raise ValueError("No videos provided to stitch")
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Check that all videos exist
        for path in video_paths:
            if not os.path.exists(path):
                raise ValueError(f"Video file not found: {path}")
        
        # Verify that all videos have the same resolution and frame rate
        if len(video_paths) > 1:
            # Get information about the first video
            cmd = [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate",
                "-of", "json", video_paths[0]
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            first_video_info = json.loads(result.stdout)
            
            try:
                first_width = first_video_info["streams"][0]["width"]
                first_height = first_video_info["streams"][0]["height"]
                first_frame_rate = first_video_info["streams"][0]["r_frame_rate"]
            except (KeyError, IndexError) as e:
                raise ValueError(f"Could not parse video info for {video_paths[0]}: {e}")
            
            # Check all other videos
            for path in video_paths[1:]:
                cmd = [
                    "ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height,r_frame_rate",
                    "-of", "json", path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                video_info = json.loads(result.stdout)
                
                try:
                    width = video_info["streams"][0]["width"]
                    height = video_info["streams"][0]["height"]
                    frame_rate = video_info["streams"][0]["r_frame_rate"]
                except (KeyError, IndexError) as e:
                    raise ValueError(f"Could not parse video info for {path}: {e}")
                
                if width != first_width or height != first_height:
                    raise ValueError(
                        f"Video resolution mismatch: {path} has {width}x{height}, "
                        f"but first video has {first_width}x{first_height}"
                    )
                
                if frame_rate != first_frame_rate:
                    raise ValueError(
                        f"Video frame rate mismatch: {path} has {frame_rate} fps, "
                        f"but first video has {first_frame_rate} fps"
                    )
        
        # Create a temporary file with the list of videos to concatenate
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            concat_list_path = f.name
            for video_path in video_paths:
                # Use absolute paths to avoid issues with paths containing spaces
                abs_path = os.path.abspath(video_path)
                # Escape single quotes in the path
                safe_path = abs_path.replace("'", "\\'")
                f.write(f"file '{safe_path}'\n")
        
        try:
            # Build the ffmpeg command
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_path,
                "-c", "copy",
                output_path
            ]
            
            # Run the ffmpeg command
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Verify that the output file exists and has size > 0
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise ValueError(f"Failed to create stitched video: {output_path}")
            
            return output_path
        
        finally:
            # Clean up the temporary file
            if os.path.exists(concat_list_path):
                os.remove(concat_list_path)
    
    async def stitch_videos_async(self, video_paths: List[str], output_path: str) -> str:
        """
        Asynchronous version of stitch_videos
        
        Args:
            video_paths: List of paths to video files to stitch together
            output_path: Path where the stitched video will be saved
        
        Returns:
            Path to the stitched video file
        """
        # Run the synchronous function in a thread pool executor
        return await asyncio.to_thread(self.stitch_videos, video_paths, output_path) 
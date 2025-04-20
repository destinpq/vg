"""
Video generation queue service for managing asynchronous video generation jobs
"""

import os
import asyncio
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from enum import Enum
from threading import Thread
import threading
from datetime import datetime
from pydantic import BaseModel, Field

from app.ai_core import HunyuanWrapper
from app.utils.config import get_settings

settings = get_settings()

class VideoStatus(str, Enum):
    """Status of video generation"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ENHANCING = "enhancing"

class VideoRequest(BaseModel):
    """Video generation request model for the queue"""
    id: str
    prompt: str
    output_path: str
    duration: float = 5.0
    fps: int = 30
    quality: str = "high"
    style: str = "realistic"
    force_replicate: bool = False
    premium_quality: bool = False
    use_hunyuan: bool = True
    subtitles: Optional[List[Dict[str, Any]]] = None
    enable_lip_sync: bool = False
    subtitle_style: Optional[Dict[str, Any]] = None
    
class VideoRequestStatus(BaseModel):
    """Status of a video generation request"""
    id: str
    status: str
    progress: float = 0
    message: str = ""
    output_path: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None
    current_stage: Optional[str] = None
    stage_progress: Optional[float] = None
    estimated_remaining_time: Optional[int] = None
    detailed_logs: List[Dict[str, Any]] = Field(default_factory=list)

class VideoQueue:
    """Queue manager for video generation jobs using Hunyuan by default"""
    
    def __init__(self):
        """Initialize the video queue"""
        self.queue = asyncio.Queue()
        self.active_requests = {}
        self.is_running = False
        self.process_task = None
        self.processor_thread = None
        
        # Initialize the model
        self.model = None
        self.settings = get_settings()
        
        # Start worker thread for model initialization
        self.processor_thread = threading.Thread(target=self._run_worker_thread, daemon=True)
        self.processor_thread.start()
        
    def _run_worker_thread(self):
        """Run the worker thread for async processing"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Initialize the model
        async def init_model():
            try:
                # Check for a bypass flag in environment
                # Used for testing without full AI backend
                if os.environ.get("DISABLE_QUEUE", "0") == "1":
                    print("Queue processor disabled via environment variable")
                    self.is_running = True
                    # Create dummy task that completes immediately
                    self.process_task = asyncio.create_task(asyncio.sleep(0))
                    return
                    
                # Initialize the AI model
                print("Initializing video generator model...")
                self.model = HunyuanWrapper(settings=self.settings)
                await self.model.initialize()
                self.is_running = True
                print("Video generator model initialized")
                
                # Start queue processor
                self.process_task = asyncio.create_task(self._process_queue())
            except Exception as e:
                print(f"Error initializing model: {e}")
                # Create a fallback task so awaits don't hang
                self.process_task = asyncio.create_task(asyncio.sleep(0))
                self.process_task.set_exception(Exception(f"Model initialization failed: {e}"))
            
        # Run the initialization
        try:
            loop.run_until_complete(init_model())
            loop.run_forever()
        except Exception as e:
            print(f"Error in worker thread: {e}")
            # Ensure we have a valid process_task even on failure
            if self.process_task is None:
                self.process_task = asyncio.Future()
                self.process_task.set_result(None)
        finally:
            loop.close()
        
    async def start_processor(self):
        """Start the queue processor"""
        if self.is_running:
            return
        
        # Only wait for worker if the process task exists and isn't done
        # Fix the NoneType issue by checking more carefully
        if self.process_task is not None and not self.process_task.done():
            try:
                await self.process_task
            except Exception as e:
                print(f"Error waiting for processor: {e}")
        else:
            # Create a dummy task for 1s to allow initialization to complete
            print("Creating fallback task since process_task is None")
            await asyncio.sleep(1)
        
        print("Video queue processor started")
        
    async def stop_processor(self):
        """Stop the queue processor"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        # Schedule stopping in the worker loop
        if self.process_task and not self.process_task.done():
            self.process_task.cancel()
            
        print("Video queue processor stopped")
        
    async def add_request(self, request: VideoRequest) -> None:
        """
        Add a new video generation request to the queue
        
        Args:
            request: VideoRequest object with all parameters needed for generation
        """
        # Initialize request status
        status = VideoRequestStatus(
            id=request.id,
            status=VideoStatus.QUEUED,
            output_path=request.output_path
        )
        
        self.active_requests[request.id] = status
        
        # Check if the processing task is initialized
        if self.process_task is None:
            # Create a simple queue - we'll process later when system is ready
            self.queue.put_nowait(request)
            print(f"Warning: Process task is None, queued {request.id} but may be delayed")
            return
        
        # Wait for queue to be ready
        if not self.process_task.done():
            try:
                await self.process_task
            except Exception as e:
                print(f"Error waiting for process task: {e}")
                # Still try to queue the request
                self.queue.put_nowait(request)
                return
        
        # Add to the queue - use a method in the worker thread to add the job
        try:
            loop = asyncio.get_event_loop()
            future = loop.create_future()
            
            # Run a task in the worker thread's event loop
            asyncio.run_coroutine_threadsafe(self._add_to_queue(request, future), self.process_task.get_loop())
            
            # Wait for the task to complete
            await future
            
            print(f"Added video job to queue: {request.id}, duration: {request.duration}s, fps: {request.fps}, quality: {request.quality}, style: {request.style}")
            print(f"Using Hunyuan: {request.use_hunyuan}, Using Replicate: {request.force_replicate}")
        except Exception as e:
            print(f"Error adding request to queue: {e}")
            # Fallback: try to add directly
            self.queue.put_nowait(request)
        
    async def _add_to_queue(self, request, future):
        """Add a request to the queue from any event loop"""
        await self.queue.put(request)
        future.set_result(True)
        
    async def get_request_status(self, request_id: str) -> Optional[VideoRequestStatus]:
        """Get the status of a video generation request"""
        return self.active_requests.get(request_id)
    
    async def update_request_progress(self, request_id: str, progress: float, message: str):
        """Update the progress of a request"""
        if request_id in self.active_requests:
            self.active_requests[request_id].progress = progress
            self.active_requests[request_id].message = message

    async def _process_queue(self):
        """Process requests in the queue"""
        while self.is_running:
            try:
                # Get the next request from the queue with timeout
                try:
                    request = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Get request details
                request_id = request.id
                if not request:
                    continue
                    
                # Update request status
                status = self.active_requests[request_id]
                status.status = VideoStatus.PROCESSING
                status.started_at = time.time()
                status.message = "Processing video generation request"
                
                # Process the request
                try:
                    print(f"Processing video request: {request_id}")
                    print(f"Prompt: {request.prompt}")
                    print(f"Duration: {request.duration}s, FPS: {request.fps}, Quality: {request.quality}, Style: {request.style}")
                    print(f"Using local GPU (Hunyuan): {request.use_hunyuan}, Using Replicate API: {request.force_replicate}")
                    
                    # Generate the video with progress tracking
                    async def progress_callback(percent, message):
                        # Parse the status message to identify the current stage
                        stage_name = "Processing"
                        stage_progress = 0.0
                        
                        # Extract stage information from the message
                        if "Initializing" in message:
                            stage_name = "Initializing"
                            stage_progress = 100.0 if percent > 15 else 50.0
                        elif "Loading" in message:
                            stage_name = "Loading Model" 
                            stage_progress = 100.0 if percent > 20 else 50.0
                        elif "Preparing" in message:
                            stage_name = "Preparing"
                            stage_progress = 100.0 if percent > 15 else 50.0
                        elif "Processing" in message or "Encoding" in message:
                            stage_name = "Processing Prompt"
                            stage_progress = 100.0 if percent > 25 else percent * 4
                        elif "Generating" in message or "latent" in message.lower():
                            stage_name = "Generating Latents"
                            stage_progress = 100.0 if percent > 30 else (percent - 25) * 20
                        elif "Diffusion" in message or "step" in message.lower():
                            stage_name = "Diffusion Steps"
                            # Extract step information if available
                            import re
                            step_match = re.search(r"step (\d+)/(\d+)", message)
                            if step_match:
                                current_step = int(step_match.group(1))
                                total_steps = int(step_match.group(2))
                                stage_progress = (current_step / total_steps) * 100
                            else:
                                stage_progress = ((percent - 30) / 60) * 100
                        elif "Rendering" in message or "frame" in message.lower():
                            stage_name = "Rendering Frames"
                            stage_progress = ((percent - 90) / 5) * 100
                        elif "Finalizing" in message or "saving" in message.lower():
                            stage_name = "Finalizing Video"
                            stage_progress = ((percent - 95) / 5) * 100
                        
                        # Ensure stage progress is between 0-100
                        stage_progress = max(0, min(100, stage_progress))
                        
                        # Update job status with detailed information
                        await self.update_job_status(
                            job_id=request_id,
                            status=VideoStatus.PROCESSING,
                            progress=percent,
                            message=message,
                            current_stage=stage_name,
                            stage_progress=stage_progress
                        )
                    
                    # Generate the video with all parameters
                    # Create video request dictionary for HunyuanWrapper
                    video_request = {
                        "id": request_id,
                        "prompt": request.prompt,
                        "duration": request.duration,
                        "fps": request.fps,
                        "quality": request.quality,
                        "style": request.style,
                        "subtitles": request.subtitles,
                        "enable_lip_sync": request.enable_lip_sync,
                        "subtitle_style": request.subtitle_style
                    }
                    
                    # Pass video request to HunyuanWrapper
                    output_path = await self.model.generate_video(
                        video_request=video_request,
                        progress_callback=progress_callback
                    )
                    
                    # Update request status
                    status.status = VideoStatus.COMPLETED
                    status.completed_at = time.time()
                    status.output_path = str(output_path)
                    status.progress = 100
                    status.message = "Video generation completed successfully"
                    
                    print(f"Completed video request: {request_id}")
                    
                except Exception as e:
                    # Update request status on error
                    status.status = VideoStatus.FAILED
                    status.error = str(e)
                    status.completed_at = time.time()
                    status.message = f"Error: {str(e)}"
                    
                    print(f"Error processing video request {request_id}: {e}")
                
                finally:
                    # Mark task as done
                    self.queue.task_done()
                    
            except asyncio.CancelledError:
                print("Video queue processor cancelled")
                break
                
            except Exception as e:
                print(f"Error in queue request processing: {e}")
                # Continue processing other requests

    async def add_job(
        self, 
        video_id: str, 
        prompt: str, 
        output_path: str,
        duration: float = 5.0, 
        fps: int = 30, 
        quality: str = "high", 
        style: str = "realistic",
        human_focus: bool = False,
        force_replicate: bool = False,
        status: str = VideoStatus.QUEUED,
        job_type: str = "standard"
    ) -> None:
        """
        Add a new video generation job to the queue with simpler parameters
        
        Args:
            video_id: Unique ID for the video
            prompt: Text prompt for the video
            output_path: Path to save the video
            duration: Duration in seconds
            fps: Frames per second
            quality: Quality setting (low, medium, high)
            style: Style setting (abstract, realistic)
            human_focus: Whether this is a human-focused video
            force_replicate: Whether to force using Replicate API
            status: Initial status
            job_type: Type of job (standard, conversation, image_to_video)
        """
        # Create the request
        request = VideoRequest(
            id=video_id,
            prompt=prompt,
            output_path=output_path,
            duration=duration,
            fps=fps,
            quality=quality,
            style=style,
            force_replicate=force_replicate or human_focus,  # Force Replicate for human videos
            premium_quality=human_focus,  # Use premium quality for human videos
            use_hunyuan=not (force_replicate or human_focus),  # Don't use Hunyuan for human videos
            subtitles=None, 
            enable_lip_sync=False
        )
        
        # Create detailed status with better tracking
        request_status = VideoRequestStatus(
            id=video_id,
            status=status,
            output_path=output_path,
            message=f"Queued for generation ({job_type} video)",
            current_stage="Preparing",
            stage_progress=0.0,
            detailed_logs=[
                {
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Job added to queue ({job_type} video)",
                    "type": "info"
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Prompt: {prompt}",
                    "type": "prompt"
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Parameters: {duration}s, {fps}fps, {quality} quality, {style} style",
                    "type": "parameter",
                    "data": {
                        "duration": duration,
                        "fps": fps,
                        "quality": quality,
                        "style": style,
                        "human_focus": human_focus,
                        "job_type": job_type
                    }
                }
            ]
        )
        
        # Add to tracking
        self.active_requests[video_id] = request_status
        
        # Add to the queue
        await self.add_request(request)
        
        return request_status

    async def update_job_status(
        self, 
        job_id: str, 
        status: str = None, 
        progress: float = None, 
        message: str = None,
        error: str = None,
        current_stage: str = None,
        stage_progress: float = None
    ):
        """
        Update the status of a job
        
        Args:
            job_id: ID of the job to update
            status: New status
            progress: New progress percentage (0-100)
            message: New status message
            error: Error message if failed
            current_stage: Current processing stage
            stage_progress: Progress within the current stage (0-100)
        """
        if job_id not in self.active_requests:
            return
            
        job_status = self.active_requests[job_id]
        
        if status:
            job_status.status = status
            
        if progress is not None:
            job_status.progress = progress
            
        if message:
            job_status.message = message
            
        if error:
            job_status.error = error
            
        if current_stage:
            job_status.current_stage = current_stage
            
        if stage_progress is not None:
            job_status.stage_progress = stage_progress
            
        # Add to detailed logs
        if message:
            log_type = "error" if status == VideoStatus.FAILED else \
                      "success" if status == VideoStatus.COMPLETED else \
                      "loading" if status == VideoStatus.PROCESSING else "info"
                      
            job_status.detailed_logs.append({
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "type": log_type
            })
            
        # Calculate estimated time
        if progress and job_status.started_at:
            elapsed = time.time() - job_status.started_at
            if progress > 0:
                estimated_total = elapsed / (progress / 100)
                remaining = estimated_total - elapsed
                job_status.estimated_remaining_time = int(remaining)
                
        # If completed, set completion time
        if status == VideoStatus.COMPLETED or status == VideoStatus.FAILED:
            job_status.completed_at = time.time()

# Create a singleton instance
video_queue = VideoQueue() 
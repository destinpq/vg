"""
Queue service for async job processing.
"""
import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable, Awaitable
import uuid

from ..config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

class VideoQueue:
    """Queue for video generation tasks."""
    
    def __init__(self):
        """Initialize the video queue."""
        self.queue = asyncio.Queue()
        self.tasks = {}
        self.results = {}
        self.status = {}
        self.is_running = False
        self.processor_task = None
    
    async def start_processor(self):
        """Start the queue processor."""
        if self.is_running:
            return
            
        self.is_running = True
        self.processor_task = asyncio.create_task(self._process_queue())
        logger.info("Video queue processor started")
    
    async def stop_processor(self):
        """Stop the queue processor."""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
        logger.info("Video queue processor stopped")
    
    async def add_task(self, task_func: Callable[[], Awaitable[Any]], **metadata) -> str:
        """Add a task to the queue."""
        task_id = str(uuid.uuid4())
        
        # Store task metadata
        self.status[task_id] = {
            "id": task_id,
            "status": "pending",
            "progress": 0,
            "created_at": time.time(),
            "started_at": None,
            "completed_at": None,
            "error": None,
            **metadata
        }
        
        # Add task to queue
        await self.queue.put((task_id, task_func))
        logger.info(f"Added task {task_id} to queue")
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task."""
        return self.status.get(task_id)
    
    async def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task."""
        return self.results.get(task_id)
    
    async def _process_queue(self):
        """Process tasks from the queue."""
        while self.is_running:
            try:
                # Get a task from the queue
                task_id, task_func = await self.queue.get()
                
                # Update task status
                self.status[task_id]["status"] = "processing"
                self.status[task_id]["started_at"] = time.time()
                
                try:
                    # Execute the task
                    logger.info(f"Processing task {task_id}")
                    result = await task_func()
                    
                    # Store the result
                    self.results[task_id] = result
                    self.status[task_id]["status"] = "completed"
                    self.status[task_id]["progress"] = 100
                    self.status[task_id]["completed_at"] = time.time()
                    
                    logger.info(f"Task {task_id} completed successfully")
                except Exception as e:
                    # Update task status on error
                    logger.exception(f"Error processing task {task_id}: {str(e)}")
                    self.status[task_id]["status"] = "failed"
                    self.status[task_id]["error"] = str(e)
                    self.status[task_id]["completed_at"] = time.time()
                
                # Mark the task as done
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in queue processor: {str(e)}")
                await asyncio.sleep(1)  # Prevent busy-looping on repeated errors

# Create a singleton instance
video_queue = VideoQueue() 
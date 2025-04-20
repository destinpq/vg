import os
import time
import threading
import logging
from typing import Dict, List, Any, Optional
import datetime

class QueueManager:
    """
    Manages a queue of video generation requests and processes them concurrently
    based on available resources
    """
    def __init__(self, max_concurrent_jobs: int = 1):
        """
        Initialize the queue manager
        
        Args:
            max_concurrent_jobs: Maximum number of concurrent generation jobs
        """
        self.logger = logging.getLogger("QueueManager")
        self.max_concurrent_jobs = max_concurrent_jobs
        self.queue = []
        self.active_generations = {}
        self.queue_lock = threading.Lock()
        self.processor_running = False
        self.stats = self._initialize_stats()
    
    def _initialize_stats(self) -> Dict[str, Any]:
        """Initialize statistics tracking"""
        return {
            "total_requests": 0,
            "completed_requests": 0,
            "failed_requests": 0,
            "total_generation_time": 0,
            "average_generation_time": 0,
            "resolutions": {},
            "daily_stats": {},
            "hourly_stats": {}
        }
    
    def add_to_queue(self, generation_id: str, generation_params: Dict[str, Any]) -> int:
        """
        Add a new generation request to the queue
        
        Args:
            generation_id: Unique ID for the generation request
            generation_params: Parameters for the generation
        
        Returns:
            Queue position
        """
        with self.queue_lock:
            queue_position = len(self.queue)
            self.queue.append(generation_id)
            
            # Initialize generation data with queued status
            self.active_generations[generation_id] = {
                "id": generation_id,
                "status": "queued",
                "queue_position": queue_position,
                "error": None,
                "created_at": datetime.datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
                "generation_time": None,
                **generation_params
            }
            
            # Update stats
            self._update_stats(self.active_generations[generation_id])
            
            # Start queue processor if not running
            self._ensure_processor_running()
            
            return queue_position
    
    def get_status(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a generation request
        
        Args:
            generation_id: ID of the generation request
        
        Returns:
            Generation status data or None if not found
        """
        return self.active_generations.get(generation_id)
    
    def get_all_generations(self) -> Dict[str, Dict[str, Any]]:
        """Get all active generations"""
        return self.active_generations
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current queue status"""
        with self.queue_lock:
            active_jobs = len([g for g in self.active_generations.values() 
                               if g["status"] == "running"])
            queued_jobs = len(self.queue)
            
            return {
                "active_jobs": active_jobs,
                "queued_jobs": queued_jobs,
                "max_concurrent_jobs": self.max_concurrent_jobs
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return self.stats
    
    def _update_stats(self, generation_info: Dict[str, Any]) -> None:
        """
        Update statistics for reporting
        
        Args:
            generation_info: Information about the generation
        """
        with self.queue_lock:
            # Update total stats
            if generation_info.get("status") == "queued" and self.active_generations[generation_info["id"]].get("status") != "queued":
                self.stats["total_requests"] += 1
            
            if generation_info.get("status") == "completed" and self.active_generations[generation_info["id"]].get("status") != "completed":
                self.stats["completed_requests"] += 1
                
                # Track generation time if available
                if "generation_time" in generation_info:
                    gen_time = generation_info["generation_time"]
                    self.stats["total_generation_time"] += gen_time
                    if self.stats["completed_requests"] > 0:
                        self.stats["average_generation_time"] = self.stats["total_generation_time"] / self.stats["completed_requests"]
                
                # Track resolution stats
                resolution = f"{generation_info.get('width', 0)}x{generation_info.get('height', 0)}"
                if resolution in self.stats["resolutions"]:
                    self.stats["resolutions"][resolution] += 1
                else:
                    self.stats["resolutions"][resolution] = 1
                    
            elif generation_info.get("status") == "failed" and self.active_generations[generation_info["id"]].get("status") != "failed":
                self.stats["failed_requests"] += 1
                
            # Update daily stats
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            if today not in self.stats["daily_stats"]:
                self.stats["daily_stats"][today] = {
                    "total": 0,
                    "completed": 0,
                    "failed": 0
                }
            
            if generation_info.get("status") == "queued" and self.active_generations[generation_info["id"]].get("status") != "queued":
                self.stats["daily_stats"][today]["total"] += 1
                
            if generation_info.get("status") == "completed" and self.active_generations[generation_info["id"]].get("status") != "completed":
                self.stats["daily_stats"][today]["completed"] += 1
                
            elif generation_info.get("status") == "failed" and self.active_generations[generation_info["id"]].get("status") != "failed":
                self.stats["daily_stats"][today]["failed"] += 1
                
            # Update hourly stats
            hour = datetime.datetime.now().strftime("%Y-%m-%d %H:00")
            if hour not in self.stats["hourly_stats"]:
                self.stats["hourly_stats"][hour] = {
                    "total": 0,
                    "completed": 0,
                    "failed": 0
                }
            
            if generation_info.get("status") == "queued" and self.active_generations[generation_info["id"]].get("status") != "queued":
                self.stats["hourly_stats"][hour]["total"] += 1
                
            if generation_info.get("status") == "completed" and self.active_generations[generation_info["id"]].get("status") != "completed":
                self.stats["hourly_stats"][hour]["completed"] += 1
                
            elif generation_info.get("status") == "failed" and self.active_generations[generation_info["id"]].get("status") != "failed":
                self.stats["hourly_stats"][hour]["failed"] += 1
    
    def update_generation(self, generation_id: str, updates: Dict[str, Any]) -> None:
        """
        Update a generation's information
        
        Args:
            generation_id: ID of the generation to update
            updates: Dictionary of fields to update
        """
        if generation_id not in self.active_generations:
            return
            
        with self.queue_lock:
            for key, value in updates.items():
                self.active_generations[generation_id][key] = value
            
            # Update stats if status changed
            if "status" in updates:
                self._update_stats(self.active_generations[generation_id])
    
    def _ensure_processor_running(self) -> None:
        """Ensure the queue processor is running"""
        if not self.processor_running:
            threading.Thread(target=self._process_queue, daemon=True).start()
    
    def _process_queue(self) -> None:
        """Process the queue of video generation requests"""
        with self.queue_lock:
            if self.processor_running:
                return
            self.processor_running = True
        
        try:
            while True:
                current_jobs = 0
                next_job = None
                
                with self.queue_lock:
                    # Count current active jobs
                    current_jobs = len([g for g in self.active_generations.values() 
                                      if g["status"] == "running"])
                    
                    # Check if we can process more jobs
                    if current_jobs < self.max_concurrent_jobs and self.queue:
                        next_job = self.queue.pop(0)
                        
                        # Update queue positions for remaining items
                        for i, job_id in enumerate(self.queue):
                            if job_id in self.active_generations:
                                self.active_generations[job_id]["queue_position"] = i
                    
                    # If no jobs to process or at capacity, exit
                    if next_job is None:
                        self.processor_running = False
                        break
                
                # Mark the job as ready for processing
                if next_job and next_job in self.active_generations:
                    self.logger.info(f"Job {next_job} is ready for processing")
                    # The actual processing will be handled by the generation handler
                    yield_job = self.active_generations[next_job]
                
                # Small delay before checking again
                time.sleep(0.5)
        
        except Exception as e:
            self.logger.error(f"Error in queue processor: {str(e)}")
        
        finally:
            with self.queue_lock:
                self.processor_running = False
    
    def mark_job_running(self, generation_id: str) -> None:
        """Mark a job as running"""
        if generation_id not in self.active_generations:
            return
            
        with self.queue_lock:
            self.active_generations[generation_id]["status"] = "running"
            self.active_generations[generation_id]["started_at"] = datetime.datetime.now().isoformat()
            self.active_generations[generation_id]["queue_position"] = 0
            self._update_stats(self.active_generations[generation_id])
    
    def mark_job_completed(self, generation_id: str, generation_time: float, output_path: str) -> None:
        """Mark a job as completed"""
        if generation_id not in self.active_generations:
            return
            
        with self.queue_lock:
            self.active_generations[generation_id]["status"] = "completed"
            self.active_generations[generation_id]["completed_at"] = datetime.datetime.now().isoformat()
            self.active_generations[generation_id]["generation_time"] = generation_time
            self.active_generations[generation_id]["video_path"] = output_path
            self._update_stats(self.active_generations[generation_id])
            
            # Restart queue processor
            self._ensure_processor_running()
    
    def mark_job_failed(self, generation_id: str, error: str) -> None:
        """Mark a job as failed"""
        if generation_id not in self.active_generations:
            return
            
        with self.queue_lock:
            self.active_generations[generation_id]["status"] = "failed"
            self.active_generations[generation_id]["completed_at"] = datetime.datetime.now().isoformat()
            self.active_generations[generation_id]["error"] = error
            self._update_stats(self.active_generations[generation_id])
            
            # Restart queue processor
            self._ensure_processor_running() 
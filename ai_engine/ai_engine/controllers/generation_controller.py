import os
import uuid
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..models.hunyuan_model import HunyuanModel
from ..models.queue_manager import QueueManager
from ..utils.preprocessing import preprocess_prompt, optimize_prompt_for_resolution

class GenerationController:
    """
    Controller for managing video generation requests
    """
    def __init__(self, model_path=None, fp8_weights_path=None, results_dir=None, max_concurrent_jobs=1):
        """
        Initialize the generation controller
        
        Args:
            model_path: Path to the model
            fp8_weights_path: Path to FP8 weights
            results_dir: Directory to store generated videos
            max_concurrent_jobs: Maximum number of concurrent generation jobs
        """
        self.logger = logging.getLogger("GenerationController")
        self.results_dir = results_dir or os.getenv("RESULTS_DIR", "./results")
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Initialize model and queue manager
        self.model = HunyuanModel(model_path, fp8_weights_path)
        self.queue_manager = QueueManager(max_concurrent_jobs)
        
        # Set up thread for processing queued jobs
        self.processing_thread = None
        self.should_process = True
        self._start_processing_thread()
    
    def _start_processing_thread(self):
        """Start the thread that processes queued generation jobs"""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.processing_thread.start()
    
    def _process_queue(self):
        """Process queued generation jobs"""
        while self.should_process:
            try:
                # Get queue status
                queue_status = self.queue_manager.get_queue_status()
                active_jobs = queue_status["active_jobs"]
                queued_jobs = queue_status["queued_jobs"]
                
                # If we're under capacity and have jobs waiting
                if active_jobs < self.queue_manager.max_concurrent_jobs and queued_jobs > 0:
                    # Find next job ready for processing
                    for generation_id, job in self.queue_manager.get_all_generations().items():
                        if job["status"] == "queued":
                            # Process this job
                            self._process_generation_job(generation_id)
                            break
            
            except Exception as e:
                self.logger.error(f"Error in queue processing: {str(e)}")
            
            # Sleep to prevent CPU hogging
            import time
            time.sleep(1)
    
    def _process_generation_job(self, generation_id):
        """
        Process a specific generation job
        
        Args:
            generation_id: ID of the generation to process
        """
        job = self.queue_manager.get_status(generation_id)
        if not job or job["status"] != "queued":
            return
        
        # Mark job as running
        self.queue_manager.mark_job_running(generation_id)
        
        try:
            # Extract parameters
            prompt = job.get("prompt", "")
            width = job.get("width", 1280)
            height = job.get("height", 720)
            video_length = job.get("video_length", 129)
            steps = job.get("steps", 50)
            seed = job.get("seed")
            guidance_scale = job.get("embedded_cfg_scale", 6.0)
            flow_shift = job.get("flow_shift", 7.0)
            flow_reverse = job.get("flow_reverse", True)
            use_fp8 = job.get("use_fp8", True)
            
            # Process prompt
            processed_prompt = preprocess_prompt(prompt)
            optimized_prompt = optimize_prompt_for_resolution(processed_prompt, width, height)
            
            # Create output path
            output_path = os.path.join(self.results_dir, f"{generation_id}.mp4")
            
            # Run generation
            result = self.model.generate_video(
                prompt=optimized_prompt,
                output_path=output_path,
                width=width,
                height=height,
                video_length=video_length,
                steps=steps,
                seed=seed,
                guidance_scale=guidance_scale,
                flow_shift=flow_shift,
                flow_reverse=flow_reverse,
                use_fp8=use_fp8
            )
            
            if result["success"]:
                # Mark job as completed
                self.queue_manager.mark_job_completed(
                    generation_id,
                    result["generation_time"],
                    result["path"]
                )
            else:
                # Mark job as failed
                self.queue_manager.mark_job_failed(
                    generation_id,
                    result.get("error", "Unknown error")
                )
        
        except Exception as e:
            self.logger.error(f"Error processing generation {generation_id}: {str(e)}")
            self.queue_manager.mark_job_failed(generation_id, str(e))
    
    def create_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new video generation request
        
        Args:
            params: Generation parameters
        
        Returns:
            Generation information
        """
        # Validate parameters
        prompt = params.get("prompt")
        if not prompt:
            return {"success": False, "error": "Missing prompt parameter"}
        
        # Create a unique ID
        generation_id = str(uuid.uuid4())
        
        # Add to queue
        queue_position = self.queue_manager.add_to_queue(generation_id, params)
        
        # Return initial information
        return {
            "id": generation_id,
            "status": "queued",
            "queue_position": queue_position
        }
    
    def get_generation_status(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific generation
        
        Args:
            generation_id: ID of the generation
        
        Returns:
            Generation status or None if not found
        """
        return self.queue_manager.get_status(generation_id)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current queue status"""
        return self.queue_manager.get_queue_status()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return self.queue_manager.get_stats()
    
    def clean_old_videos(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Clean up old generated videos to free disk space
        
        Args:
            max_age_hours: Maximum age of videos to keep (in hours)
            
        Returns:
            Cleanup statistics
        """
        import time
        
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        
        # Find videos older than the specified age
        deleted_count = 0
        preserved_count = 0
        
        for file in os.listdir(self.results_dir):
            if file.endswith('.mp4'):
                file_path = os.path.join(self.results_dir, file)
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    # Check if it's safe to delete (not in use)
                    file_id = os.path.splitext(file)[0]
                    is_active = False
                    
                    for gen in self.queue_manager.get_all_generations().values():
                        if gen["status"] == "running" and gen.get("video_path") == file_path:
                            is_active = True
                            break
                    
                    if not is_active:
                        os.remove(file_path)
                        deleted_count += 1
                else:
                    preserved_count += 1
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "preserved_count": preserved_count,
            "max_age_hours": max_age_hours
        } 
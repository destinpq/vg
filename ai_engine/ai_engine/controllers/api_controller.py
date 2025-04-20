import os
import logging
from typing import Dict, Any, Optional
from flask import send_file, jsonify, request

from .generation_controller import GenerationController

class ApiController:
    """
    Controller for handling API requests related to video generation
    """
    def __init__(self, generation_controller: Optional[GenerationController] = None):
        """
        Initialize the API controller
        
        Args:
            generation_controller: Controller for video generation, or None to create a new one
        """
        self.logger = logging.getLogger("ApiController")
        self.generation_controller = generation_controller or GenerationController(
            model_path=os.getenv("HUNYUANVIDEO_MODEL_PATH"),
            fp8_weights_path=os.getenv("FP8_WEIGHTS_PATH"),
            results_dir=os.getenv("RESULTS_DIR", "./results"),
            max_concurrent_jobs=int(os.getenv("MAX_CONCURRENT_JOBS", "1"))
        )
    
    def get_supported_resolutions(self) -> Dict[str, Any]:
        """Get supported video resolutions"""
        return {
            "resolutions": [
                {
                    "width": 1920,
                    "height": 1080,
                    "name": "Full HD (1080p)",
                    "quality": "High",
                    "recommended_memory_gb": 40
                },
                {
                    "width": 1280,
                    "height": 720,
                    "name": "HD (720p)",
                    "quality": "Good",
                    "recommended_memory_gb": 24
                },
                {
                    "width": 960,
                    "height": 544,
                    "name": "SD (544p)",
                    "quality": "Medium",
                    "recommended_memory_gb": 16 
                },
                {
                    "width": 720,
                    "height": 720,
                    "name": "Square",
                    "quality": "Good",
                    "recommended_memory_gb": 20
                }
            ]
        }
    
    def handle_generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a video generation request
        
        Args:
            data: Request data containing generation parameters
            
        Returns:
            Response data
        """
        try:
            # Validate input
            if not data or 'prompt' not in data:
                return {"error": "Missing prompt in request"}, 400
            
            # Extract parameters with defaults
            params = {
                "prompt": data['prompt'],
                "width": data.get('width', 1280),
                "height": data.get('height', 720),
                "video_length": data.get('video_length', 129),
                "steps": data.get('steps', 50),
                "seed": data.get('seed'),
                "embedded_cfg_scale": data.get('embedded_cfg_scale', 6.0),
                "flow_shift": data.get('flow_shift', 7.0),
                "flow_reverse": data.get('flow_reverse', True),
                "use_fp8": data.get('use_fp8', True)
            }
            
            # Check if resolution is supported
            supported_resolutions = [
                (1920, 1080),  # Full HD
                (1280, 720),   # HD
                (960, 544),    # SD
                (720, 720)     # Square
            ]
            
            if (params["width"], params["height"]) not in supported_resolutions:
                return {
                    "error": f"Unsupported resolution: {params['width']}x{params['height']}. Please use one of the supported resolutions."
                }, 400
            
            # Create generation
            result = self.generation_controller.create_generation(params)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error starting generation: {str(e)}")
            return {"error": str(e)}, 500
    
    def handle_status(self, generation_id: str) -> Dict[str, Any]:
        """
        Handle a status request for a specific generation
        
        Args:
            generation_id: ID of the generation
            
        Returns:
            Status information
        """
        try:
            status = self.generation_controller.get_generation_status(generation_id)
            
            if not status:
                return {"error": "Generation ID not found"}, 404
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting status: {str(e)}")
            return {"error": str(e)}, 500
    
    def handle_video(self, generation_id: str):
        """
        Handle a request to get a generated video
        
        Args:
            generation_id: ID of the generation
            
        Returns:
            Video file or error response
        """
        try:
            status = self.generation_controller.get_generation_status(generation_id)
            
            if not status:
                return {"error": "Generation ID not found"}, 404
            
            if status["status"] != "completed":
                return {"error": f"Video generation is {status['status']}"}, 400
            
            video_path = status.get("video_path")
            if not video_path or not os.path.exists(video_path):
                return {"error": "Video file not found"}, 404
            
            return send_file(video_path, mimetype='video/mp4')
            
        except Exception as e:
            self.logger.error(f"Error getting video: {str(e)}")
            return {"error": str(e)}, 500
    
    def handle_queue_status(self) -> Dict[str, Any]:
        """
        Handle a request to get the current queue status
        
        Returns:
            Queue status information
        """
        try:
            return self.generation_controller.get_queue_status()
            
        except Exception as e:
            self.logger.error(f"Error getting queue status: {str(e)}")
            return {"error": str(e)}, 500
    
    def handle_stats(self) -> Dict[str, Any]:
        """
        Handle a request to get generation statistics
        
        Returns:
            Statistics information
        """
        try:
            return self.generation_controller.get_stats()
            
        except Exception as e:
            self.logger.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)}, 500
    
    def handle_clean_videos(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a request to clean up old videos
        
        Args:
            data: Request data containing cleanup parameters
            
        Returns:
            Cleanup results
        """
        try:
            max_age_hours = data.get('max_age_hours', 24)
            
            return self.generation_controller.clean_old_videos(max_age_hours)
            
        except Exception as e:
            self.logger.error(f"Error cleaning videos: {str(e)}")
            return {"error": str(e)}, 500
    
    def handle_gpu_status(self) -> Dict[str, Any]:
        """
        Handle a request to get GPU status information
        
        Returns:
            GPU status information
        """
        try:
            # Get GPU info from model
            gpu_info = self.generation_controller.model.get_gpu_memory_info()
            
            # Get queue info
            active_jobs = len([g for g in self.generation_controller.queue_manager.get_all_generations().values() 
                             if g["status"] == "running"])
            queued_jobs = len(self.generation_controller.queue_manager.queue)
            completed_jobs = len([g for g in self.generation_controller.queue_manager.get_all_generations().values() 
                                if g["status"] == "completed"])
            
            return {
                "gpu_info": gpu_info,
                "active_jobs": active_jobs,
                "queued_jobs": queued_jobs,
                "completed_jobs": completed_jobs
            }
            
        except Exception as e:
            self.logger.error(f"Error getting GPU status: {str(e)}")
            return {"error": str(e)}, 500 
"""
Hunyuan video generation service.
"""
import os
import time
import logging
import base64
from pathlib import Path
from typing import Dict, Any, Optional
import requests
from datetime import datetime

from ..config.settings import settings
from .log_service import log_service

# Configure logging
logger = logging.getLogger(__name__)

class HunyuanService:
    """Service for generating videos using Hunyuan API."""
    
    def __init__(self):
        """Initialize the Hunyuan service."""
        self.api_url = settings.HUNYUAN_API_URL
        self.health_url = f"{self.api_url}/health"
        self.generate_url = f"{self.api_url}/generate-video"
        self.output_dir = Path(settings.OUTPUT_DIR)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Hunyuan service initialized with API URL: {self.api_url}")
        
    async def check_health(self) -> Dict[str, Any]:
        """Check if the Hunyuan API is healthy."""
        try:
            response = requests.get(self.health_url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Health check failed with status code {response.status_code}")
                return {"status": "unhealthy", "error": response.text}
        except Exception as e:
            logger.error(f"Error checking Hunyuan API health: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def generate_video(self, 
                           prompt: str,
                           num_inference_steps: int = 50,
                           height: int = 320,
                           width: int = 576,
                           output_format: str = "gif") -> Dict[str, Any]:
        """Generate a video using the Hunyuan API."""
        # Start timing for logging
        start_time = datetime.utcnow()
        generation_time_ms = None
        
        # Create a unique ID for this request
        request_id = f"hunyuan_{int(time.time())}"
        
        # Log the video generation request
        log_entry = await log_service.log_activity({
            "endpoint": "hunyuan/generate",
            "method": "POST",
            "path": "/hunyuan/generate",
            "start_time": start_time,
            "request_data": {
                "prompt": prompt,
                "num_inference_steps": num_inference_steps,
                "height": height,
                "width": width,
                "output_format": output_format
            },
            "metadata": {
                "request_id": request_id,
                "generation_type": "hunyuan_video"
            }
        })
        
        try:
            logger.info(f"Generating video for prompt: '{prompt}'")
            
            # Prepare the request data
            data = {
                "prompt": prompt,
                "num_inference_steps": num_inference_steps,
                "height": height,
                "width": width,
                "output_format": output_format
            }
            
            # Make the request to the API
            logger.info(f"Sending request to {self.generate_url}")
            response = requests.post(self.generate_url, json=data, timeout=300)  # 5 minute timeout
            
            # Calculate generation time
            end_time = datetime.utcnow()
            generation_time_ms = (end_time - start_time).total_seconds() * 1000
            
            if response.status_code != 200:
                logger.error(f"Error generating video: {response.status_code}")
                logger.error(response.text)
                
                # Log the error
                if log_entry:
                    await log_service.log_response(
                        log_entry,
                        response.status_code,
                        error=f"API returned status code {response.status_code}: {response.text}"
                    )
                
                return {
                    "success": False, 
                    "error": f"API returned status code {response.status_code}",
                    "details": response.text
                }
            
            # Parse the response
            result = response.json()
            
            # If the API returned base64 encoded video data, decode and save it
            if "video_base64" in result:
                output_dir = self.output_dir / request_id
                output_dir.mkdir(exist_ok=True, parents=True)
                
                # Decode and save the video
                video_data = base64.b64decode(result["video_base64"])
                ext = "gif" if output_format == "gif" else "mp4"
                output_file = output_dir / f"generated_video.{ext}"
                
                with open(output_file, "wb") as f:
                    f.write(video_data)
                
                # Update the result with the local file path
                result["local_video_path"] = str(output_file)
                result["web_video_path"] = f"/{settings.OUTPUT_DIR}/{request_id}/generated_video.{ext}"
                
                # Remove the base64 data to save memory
                del result["video_base64"]
            
            # Log successful response
            if log_entry:
                await log_service.log_response(
                    log_entry,
                    response.status_code,
                    response_data={
                        "success": True,
                        "request_id": request_id,
                        "generation_time_ms": generation_time_ms,
                        "output_path": result.get("web_video_path", None)
                    }
                )
            
            # Add generation time to the result
            result_with_meta = {
                "success": True,
                "request_id": request_id,
                "result": result,
                "generation_time_ms": generation_time_ms
            }
            
            return result_with_meta
            
        except Exception as e:
            logger.error(f"Error communicating with Hunyuan API: {str(e)}")
            
            # Log the error
            if log_entry:
                await log_service.log_response(
                    log_entry,
                    500,
                    error=str(e)
                )
            
            return {"success": False, "error": str(e)}

# Create a singleton instance
hunyuan_service = HunyuanService() 
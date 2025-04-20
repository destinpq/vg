#!/usr/bin/env python3
"""
Client for communicating with the Hunyuan API running on the H100 GPU.
This module provides functions to make requests to the Hunyuan API for video generation.
"""
import os
import time
import requests
import logging
import json
import base64
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_HUNYUAN_API_URL = os.environ.get('HUNYUAN_API_URL', 'http://your-h100-gpu-ip:8000')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'output')

class HunyuanClient:
    """Client for communicating with the Hunyuan API on the H100 GPU"""
    
    def __init__(self, api_url=None):
        """Initialize the client with the API URL"""
        self.api_url = api_url or DEFAULT_HUNYUAN_API_URL
        self.health_url = f"{self.api_url}/health"
        self.generate_url = f"{self.api_url}/generate-video"
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
    def check_health(self):
        """Check if the Hunyuan API is healthy"""
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
    
    def generate_video(self, prompt, num_inference_steps=50, height=320, width=576, output_format="gif"):
        """Generate a video using the Hunyuan API
        
        Args:
            prompt (str): The text prompt for generating the video
            num_inference_steps (int): Number of inference steps
            height (int): Height of the video
            width (int): Width of the video
            output_format (str): Output format (gif or mp4)
            
        Returns:
            dict: Response from the API with video information
        """
        try:
            logger.info(f"Generating video for prompt: '{prompt}'")
            
            # Create a unique ID for this request
            request_id = f"hunyuan_{int(time.time())}"
            
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
            
            if response.status_code != 200:
                logger.error(f"Error generating video: {response.status_code}")
                logger.error(response.text)
                return {
                    "success": False, 
                    "error": f"API returned status code {response.status_code}",
                    "details": response.text
                }
            
            # Parse the response
            result = response.json()
            
            # If the API returned base64 encoded video data, decode and save it
            if "video_base64" in result:
                output_dir = Path(OUTPUT_DIR) / request_id
                output_dir.mkdir(exist_ok=True, parents=True)
                
                # Decode and save the video
                video_data = base64.b64decode(result["video_base64"])
                ext = "gif" if output_format == "gif" else "mp4"
                output_file = output_dir / f"generated_video.{ext}"
                
                with open(output_file, "wb") as f:
                    f.write(video_data)
                
                # Update the result with the local file path
                result["local_video_path"] = str(output_file)
                result["web_video_path"] = f"/{OUTPUT_DIR}/{request_id}/generated_video.{ext}"
                
                # Remove the base64 data to save memory
                del result["video_base64"]
            
            return {
                "success": True,
                "request_id": request_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error communicating with Hunyuan API: {str(e)}")
            return {"success": False, "error": str(e)}

# Create a singleton instance
hunyuan_client = HunyuanClient()

def test_client():
    """Test the Hunyuan client"""
    client = HunyuanClient()
    
    # Check health
    health = client.check_health()
    print("Health check result:", json.dumps(health, indent=2))
    
    if health.get("status") == "healthy":
        # Generate a test video
        prompt = "A cat playing piano, cinematic quality, 4K"
        result = client.generate_video(prompt)
        print("Generation result:", json.dumps(result, indent=2))
    
if __name__ == "__main__":
    test_client() 
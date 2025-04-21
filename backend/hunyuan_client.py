#!/usr/bin/env python3
"""
Hunyuan Client for backwards compatibility.
This module forwards to app.clients.hunyuan_client for MVC structure.
"""
from app.clients.hunyuan_client import hunyuan_client, HunyuanClient

# Expose the same functions and classes for backward compatibility
__all__ = ["hunyuan_client", "HunyuanClient"]

# For direct import
if __name__ == "__main__":
    # Testing code
    import json
    
    client = HunyuanClient()
    
    # Check health
    health = client.check_health()
    print("Health check result:", json.dumps(health, indent=2))
    
    if health.get("status") == "healthy":
        # Generate a test video
        prompt = "A cat playing piano, cinematic quality, 4K"
        result = client.generate_video(prompt)
        print("Generation result:", json.dumps(result, indent=2))

"""
Simple client for the Hunyuan Video API.
"""
import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.hunyuan')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API URL from environment
HUNYUAN_API_URL = os.getenv('HUNYUAN_API_URL', 'http://192.241.176.107:8000')

def check_health():
    """Check if the Hunyuan API is healthy."""
    try:
        response = requests.get(f"{HUNYUAN_API_URL}/health", timeout=5)
        return response.json() if response.status_code == 200 else {"status": "error", "message": response.text}
    except Exception as e:
        logger.error(f"Error checking Hunyuan API health: {e}")
        return {"status": "error", "message": str(e)}

def generate_video(prompt, num_inference_steps=50, height=320, width=576, output_format="mp4"):
    """Generate a video using the Hunyuan API."""
    try:
        data = {
            "prompt": prompt,
            "num_inference_steps": num_inference_steps,
            "height": height,
            "width": width,
            "output_format": output_format
        }
        
        logger.info(f"Sending request to Hunyuan API at {HUNYUAN_API_URL}/generate-video")
        logger.info(f"Prompt: {prompt}")
        
        response = requests.post(
            f"{HUNYUAN_API_URL}/generate-video", 
            json=data, 
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code != 200:
            logger.error(f"Error from Hunyuan API: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text}
            
        return {"success": True, "result": response.json()}
        
    except Exception as e:
        logger.error(f"Error calling Hunyuan API: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test the client
    health = check_health()
    print(f"API Health: {health}")
    
    if health.get("status") == "healthy":
        result = generate_video("A beautiful sunset over the ocean", num_inference_steps=30)
        print(f"Generation result: {result}") 
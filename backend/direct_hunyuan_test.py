#!/usr/bin/env python
"""
Direct test client for the Hunyuan Video API.
This is a standalone script with no dependencies on the rest of the codebase.
"""
import os
import json
import requests
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use Digital Ocean GPU server directly
HUNYUAN_API_URL = "http://192.241.176.107:8000"
logger.info(f"Using Hunyuan API at: {HUNYUAN_API_URL}")

def check_health():
    """Check if the Hunyuan API is healthy."""
    try:
        logger.info(f"Checking health at {HUNYUAN_API_URL}/health")
        response = requests.get(f"{HUNYUAN_API_URL}/health", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Health check failed with status {response.status_code}: {response.text}")
            return {"status": "error", "message": response.text}
    except Exception as e:
        logger.error(f"Error checking Hunyuan API health: {e}")
        return {"status": "error", "message": str(e)}

def generate_video(prompt, num_inference_steps=30, height=320, width=576, output_format="mp4"):
    """Generate a video using the Hunyuan API."""
    try:
        data = {
            "prompt": prompt,
            "num_inference_steps": num_inference_steps,
            "height": height,
            "width": width,
            "output_format": output_format
        }
        
        logger.info(f"Sending request to {HUNYUAN_API_URL}/generate-video")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Parameters: steps={num_inference_steps}, size={width}x{height}, format={output_format}")
        
        response = requests.post(
            f"{HUNYUAN_API_URL}/generate-video", 
            json=data, 
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code != 200:
            logger.error(f"Error from Hunyuan API: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text}
        
        result = response.json()
        logger.info(f"Video generated successfully")
        return {"success": True, "result": result}
        
    except Exception as e:
        logger.error(f"Error calling Hunyuan API: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Test the API health
    logger.info("=== Testing Hunyuan API Connection ===")
    health = check_health()
    print(f"API Health: {json.dumps(health, indent=2)}")
    
    if health.get("status") == "healthy" or health.get("status") == "ok":
        logger.info("API is healthy, testing video generation...")
        # Now test video generation with a simple prompt
        result = generate_video(
            prompt="A beautiful sunset over the ocean with sailboats", 
            num_inference_steps=30,
            height=320, 
            width=576
        )
        print(f"Generation result: {json.dumps(result, indent=2)}")
    else:
        logger.error("API is not healthy. Please check the GPU server status.") 
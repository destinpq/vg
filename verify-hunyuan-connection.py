#!/usr/bin/env python3
"""
Script to verify that the backend can communicate with the Hunyuan API on the H100 GPU.
This script performs:
1. Health check to verify the API is running
2. Test video generation to verify the API is working correctly
"""
import os
import sys
import json
import time
import base64
import requests
import argparse
from pathlib import Path

# Configure defaults
DEFAULT_API_URL = "http://localhost:8000"
OUTPUT_DIR = "hunyuan_test_output"

def setup():
    """Set up the test environment"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Test output will be saved to: {OUTPUT_DIR}")

def check_health(api_url):
    """Check the health of the Hunyuan API"""
    health_url = f"{api_url}/health"
    print(f"Checking health status at: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        response.raise_for_status()
        
        health_data = response.json()
        print(f"API Status: {health_data.get('status', 'unknown')}")
        print(f"Model Loaded: {health_data.get('model_loaded', False)}")
        
        if 'gpu_info' in health_data and health_data['gpu_info']:
            gpu_info = health_data['gpu_info']
            print("\nGPU Information:")
            print(f"  Name: {gpu_info.get('name', 'unknown')}")
            print(f"  Memory Allocated: {gpu_info.get('memory_allocated_gb', 0)} GB")
            print(f"  Memory Reserved: {gpu_info.get('memory_reserved_gb', 0)} GB")
            print(f"  Total Memory: {gpu_info.get('total_memory_gb', 0)} GB")
        
        return health_data.get('status') == 'healthy' and health_data.get('model_loaded', False)
    
    except requests.exceptions.RequestException as e:
        print(f"Error checking health: {e}")
        return False

def generate_test_video(api_url, prompt="A cat walking in a garden, high quality, cinematic"):
    """Generate a test video to verify the API is working correctly"""
    generate_url = f"{api_url}/generate-video"
    print(f"\nGenerating test video at: {generate_url}")
    print(f"Prompt: '{prompt}'")
    
    start_time = time.time()
    
    try:
        # Set up parameters - using lower quality for a quicker test
        params = {
            "prompt": prompt,
            "width": 320,  # Smaller for faster testing
            "height": 192,  # Smaller for faster testing
            "num_inference_steps": 20,  # Fewer steps for faster testing
            "video_length": 16,  # Shorter video for faster testing
        }
        
        print("Sending request with parameters:")
        print(json.dumps(params, indent=2))
        
        # Send request
        response = requests.post(generate_url, json=params, timeout=300)  # 5 minute timeout
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        # Save output
        if "video_base64" in result:
            # Decode video
            video_data = base64.b64decode(result["video_base64"])
            
            # Save to file
            output_file = Path(OUTPUT_DIR) / "test_video.gif"
            with open(output_file, "wb") as f:
                f.write(video_data)
            
            print(f"\nTest video saved to: {output_file}")
            print(f"Generation time: {result.get('generation_time_seconds', 0):.2f} seconds")
            
            return True
        else:
            print("\nError: No video data in response")
            print(f"Response: {json.dumps(result, indent=2)}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\nError generating video: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                print(f"Response: {e.response.json()}")
            except:
                print(f"Response text: {e.response.text}")
        return False
    finally:
        elapsed = time.time() - start_time
        print(f"Total request time: {elapsed:.2f} seconds")

def main():
    """Main function to run the test"""
    parser = argparse.ArgumentParser(description="Verify connection to Hunyuan API")
    parser.add_argument("--api-url", type=str, default=DEFAULT_API_URL, help="URL of the Hunyuan API")
    parser.add_argument("--prompt", type=str, default=None, help="Test prompt to use for video generation")
    args = parser.parse_args()
    
    api_url = args.api_url
    prompt = args.prompt or "A cat walking in a garden, high quality, cinematic"
    
    print("=" * 60)
    print(f"Verifying connection to Hunyuan API at: {api_url}")
    print("=" * 60)
    
    # Set up output directory
    setup()
    
    # Check health
    print("\nStep 1: Checking API health")
    health_ok = check_health(api_url)
    
    if not health_ok:
        print("\nHealth check failed! Please check the Hunyuan API service.")
        sys.exit(1)
    
    print("\nStep 2: Generating test video")
    generation_ok = generate_test_video(api_url, prompt)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if health_ok and generation_ok:
        print("✅ Connection to Hunyuan API successful!")
        print("✅ Test video generation successful!")
        print("\n🎉 Your Hunyuan Video setup is working correctly!")
        
        print("\nNext Steps:")
        print("1. Update your .env file with HUNYUAN_API_URL=" + api_url)
        print("2. Restart your backend service to start using Hunyuan Video")
    else:
        if not health_ok:
            print("❌ Health check failed!")
        if not generation_ok:
            print("❌ Test video generation failed!")
        
        print("\nPlease check the logs and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
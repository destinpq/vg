from flask import Blueprint, request, jsonify
import os
import time
import logging
from pathlib import Path
from ..utils.config import get_settings
from ..services.video_queue import video_queue
from ...hunyuan_client import hunyuan_client

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
router = Blueprint('hunyuan', __name__)

# Get settings
settings = get_settings()

@router.route("/status", methods=["GET"])
async def check_hunyuan_status():
    """Check the status of the Hunyuan API"""
    logger.info("Checking Hunyuan API status")
    
    # Check the status of the Hunyuan API
    health_status = hunyuan_client.check_health()
    
    return jsonify({
        "status": "ok" if health_status.get("status") == "healthy" else "error",
        "hunyuan_api": health_status,
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@router.route("/generate", methods=["POST"])
async def generate_hunyuan_video():
    """Generate a video using the Hunyuan model on H100 GPU"""
    try:
        # Get parameters from request
        data = request.json or {}
        
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Get optional parameters with defaults
        num_inference_steps = int(data.get("num_inference_steps", 50))
        height = int(data.get("height", 320))
        width = int(data.get("width", 576))
        output_format = data.get("output_format", "gif")
        
        # Set reasonable limits
        if num_inference_steps > 100:
            num_inference_steps = 100
        
        if height > 640:
            height = 640
        
        if width > 1024:
            width = 1024
        
        # Generate a unique ID for this request
        request_id = f"hunyuan_{int(time.time())}"
        
        # Add task to the queue
        async def generate_task():
            # Generate the video
            result = hunyuan_client.generate_video(
                prompt=prompt,
                num_inference_steps=num_inference_steps,
                height=height,
                width=width,
                output_format=output_format
            )
            
            # Return the result
            return result
        
        # Add the task to the queue
        task_id = await video_queue.add_task(
            generate_task,
            prompt=prompt,
            task_type="hunyuan",
            request_id=request_id
        )
        
        # Return the initial response
        return jsonify({
            "status": "pending",
            "request_id": request_id,
            "task_id": task_id,
            "message": "Video generation task added to queue",
            "prompt": prompt,
            "parameters": {
                "num_inference_steps": num_inference_steps,
                "height": height,
                "width": width,
                "output_format": output_format
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating Hunyuan video: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500 
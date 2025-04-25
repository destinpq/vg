from flask import Flask, jsonify, request
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create the Flask app
flask_app = Flask(__name__)

# Import Hunyuan client (for backward compatibility)
try:
    from .services.hunyuan_service import HunyuanService
    hunyuan_service = HunyuanService()
except ImportError:
    logger.warning("Could not import HunyuanService, using mock implementation")
    hunyuan_service = None

@flask_app.route("/health")
def health_check():
    """Health check endpoint for Flask app"""
    return jsonify({
        "status": "ok",
        "service": "flask_app"
    })

@flask_app.route("/hunyuan/status", methods=["GET"])
def check_hunyuan_status():
    """Check the status of the Hunyuan API (legacy endpoint)"""
    logger.info("Checking Hunyuan API status")
    
    if not hunyuan_service:
        return jsonify({
            "status": "error",
            "message": "Hunyuan service not available"
        }), 503
    
    # Check the status of the Hunyuan API
    health_status = hunyuan_service.check_health()
    
    return jsonify({
        "status": "ok" if health_status.get("status") == "healthy" else "error",
        "hunyuan_api": health_status,
    })

@flask_app.route("/hunyuan/generate", methods=["POST"])
def generate_hunyuan_video():
    """Generate a video using Hunyuan (legacy endpoint)"""
    if not hunyuan_service:
        return jsonify({
            "status": "error",
            "message": "Hunyuan service not available"
        }), 503
    
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
        output_format = data.get("output_format", "mp4")
        
        # Generate the video
        result = hunyuan_service.generate_video(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            height=height,
            width=width,
            output_format=output_format
        )
        
        if result.get("success", False):
            return jsonify({
                "status": "success",
                "message": "Video generation completed",
                "result": result.get("result", {})
            })
        else:
            return jsonify({
                "status": "error",
                "message": result.get("error", "Unknown error")
            }), 500
            
    except Exception as e:
        logger.error(f"Error generating Hunyuan video: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@flask_app.route("/api/legacy", methods=["GET"])
def legacy_info():
    """Information about legacy endpoints"""
    return jsonify({
        "message": "This is the legacy Flask API, please use the FastAPI endpoints for new development",
        "endpoints": {
            "health": "/health",
            "hunyuan_status": "/hunyuan/status",
            "hunyuan_generate": "/hunyuan/generate"
        }
    }) 
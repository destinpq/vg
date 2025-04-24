import os
import json
import uuid
import time
import random
import logging
import asyncio
import re
from pathlib import Path
from dotenv import load_dotenv
# For async support in Flask
import threading
from functools import wraps
import traceback

from flask import Flask, request, jsonify, send_from_directory, redirect, Response
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Handle OpenAI API Key
openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    print(f"OpenAI API key set from environment variables, length: {len(openai_api_key)}")
else:
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    openai_api_key = line.strip().split("=", 1)[1].strip()
                    # Remove quotes if present
                    if openai_api_key.startswith('"') and openai_api_key.endswith('"'):
                        openai_api_key = openai_api_key[1:-1]
                    elif openai_api_key.startswith("'") and openai_api_key.endswith("'"):
                        openai_api_key = openai_api_key[1:-1]
                    os.environ["OPENAI_API_KEY"] = openai_api_key
                    print(f"OpenAI API key loaded from .env file, length: {len(openai_api_key)}")
                    break
    except Exception as e:
        print(f"Error loading OpenAI API key from .env file: {e}")

# Create output directory if it doesn't exist
output_dir = Path(os.environ.get("OUTPUT_DIR", "./output"))
outputs_dir = Path("outputs")
os.makedirs(output_dir, exist_ok=True)
print(f"Static file serving from directory: {output_dir}")

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory storage for tracking video job status
video_jobs = {}

def generate_prediction_id():
    return str(uuid.uuid4())

def process_video_job(prediction_id, model_id, params):
    """Process video job in a separate thread"""
    try:
        # Update status to processing
        video_jobs[prediction_id]['status'] = 'processing'
        video_jobs[prediction_id]['logs'] = "Started processing video..."
        
        # Get parameters from the request
        force_replicate = params.get('force_replicate', False)
        prompt = params.get('prompt', '')
        duration = params.get('duration', 5)
        quality = params.get('quality', 'high')
        style = params.get('style', 'cinematic')
        human_focus = params.get('human_focus', False)
        
        # Log the parameters
        video_jobs[prediction_id]['logs'] += f"\nParameters: {json.dumps(params, indent=2)}"
        
        if force_replicate:
            # Check if Replicate API token is set
            replicate_token = os.environ.get("REPLICATE_API_TOKEN")
            if not replicate_token:
                video_jobs[prediction_id]['status'] = 'failed'
                video_jobs[prediction_id]['logs'] += "\nReplicate API token not set. Please set REPLICATE_API_TOKEN in .env file."
                return
            
            # Call Replicate API
            video_jobs[prediction_id]['logs'] += "\nCalling Replicate API..."
            
            try:
                # Install replicate if not already installed
                try:
                    import replicate
                except ImportError:
                    import pip
                    pip.main(['install', 'replicate'])
                    import replicate
                
                # Set the Replicate API token
                os.environ["REPLICATE_API_TOKEN"] = replicate_token
                video_jobs[prediction_id]['logs'] += f"\nUsing Replicate API token: {replicate_token[:4]}...{replicate_token[-4:]}"
                
                # The user requested a specific Tencent Hunyuan version
                tencent_model_id = "tencent/hunyuan-video:6c9132aee14409cd6568d030453f1ba50f5f3412b844fe67f78a9eb62d55664f"
                
                video_jobs[prediction_id]['logs'] += f"\nUsing specified Tencent Hunyuan Video model: {tencent_model_id}"
                
                # Create parameters for Tencent Hunyuan video model
                hunyuan_params = {
                    "prompt": prompt,
                    "negative_prompt": "low quality, blurry, noisy, text, watermark, signature, low-res, bad anatomy, bad proportions, deformed body, duplicate, extra limbs",
                    "num_frames": min(96, int(float(duration)) * 24),  # Cap at 96 frames
                    "width": 1280,
                    "height": 720,
                    "fps": 24,
                    "guidance_scale": 9.0,
                    "num_inference_steps": 50,
                    "seed": random.randint(1, 100000)
                }
                
                video_jobs[prediction_id]['logs'] += f"\nHunyuan model parameters: {json.dumps(hunyuan_params, indent=2)}"
                
                # Use the complete model ID format with parameters for this model
                try:
                    # Try the Tencent Hunyuan model with the specified version
                    output = replicate.run(
                        tencent_model_id,
                        input=hunyuan_params
                    )
                except Exception as e:
                    # Log the error but try a second model
                    video_jobs[prediction_id]['logs'] += f"\nFirst model error: {str(e)}"
                    video_jobs[prediction_id]['logs'] += f"\nTrying fallback text-to-video model..."
                    
                    # Use a different, even more widely available model as fallback
                    fallback_model_id = "cjwbw/damo-text-to-video:1e205ea73084bd39a2174014e447edd5e40e43f665fae5b35e9af2166a0c2f73"
                    
                    fallback_params = {
                        "prompt": prompt,
                        "negative_prompt": "low quality, blurry",
                        "num_inference_steps": 50,
                        "guidance_scale": 9.0,
                        "random_seed": random.randint(1, 100000),
                        "width": 1024,
                        "height": 576
                    }
                    
                    video_jobs[prediction_id]['logs'] += f"\nUsing fallback model: {fallback_model_id}"
                    
                    # Try the fallback model
                    output = replicate.run(
                        fallback_model_id,
                        input=fallback_params
                    )
                
                # The prediction output will be a URL to the generated video
                if isinstance(output, list):
                    video_url = output[0]
                else:
                    video_url = output
                
                video_jobs[prediction_id]['logs'] += f"\nVideo URL: {video_url}"
                
                # Download the video
                video_jobs[prediction_id]['logs'] += "\nDownloading video..."
                
                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
                    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{prediction_id}.mp4")
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # Update status to succeeded
                    video_jobs[prediction_id]['status'] = 'succeeded'
                    video_jobs[prediction_id]['output_path'] = output_path
                    video_jobs[prediction_id]['logs'] += "\nVideo downloaded successfully."
                else:
                    raise Exception(f"Failed to download video: HTTP {response.status_code}")
                
            except Exception as e:
                video_jobs[prediction_id]['status'] = 'failed'
                video_jobs[prediction_id]['logs'] += f"\nReplicate API error: {str(e)}\n{traceback.format_exc()}"
                return
        else:
            # If not using Replicate, just create a dummy video (for testing)
            video_jobs[prediction_id]['logs'] += "\nCreating dummy video (Replicate not enabled)..."
            time.sleep(5)  # Simulate work
            
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{prediction_id}.mp4")
            
            # For demo, create an empty file with some basic content
            with open(output_path, 'wb') as f:
                f.write(b'Dummy video content - Enable Replicate for real video generation')
            
            # Update status to succeeded
            video_jobs[prediction_id]['status'] = 'succeeded'
            video_jobs[prediction_id]['output_path'] = output_path
            video_jobs[prediction_id]['logs'] += "\nDummy video created successfully."
    
    except Exception as e:
        # Update status to failed
        video_jobs[prediction_id]['status'] = 'failed'
        video_jobs[prediction_id]['logs'] = f"Error: {str(e)}\n{traceback.format_exc()}"

def json_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return decorated_function

@app.route('/video', methods=['POST'])
@json_response
def generate_video():
    data = request.json or {}
    model_id = data.get('model_id', 'default-model')
    
    # Generate a unique prediction ID
    prediction_id = generate_prediction_id()
    
    # Store job information
    video_jobs[prediction_id] = {
        'status': 'pending',
        'created_at': time.time(),
        'updated_at': time.time(),
        'model_id': model_id,
        'params': data,
        'logs': "Job created, waiting to start processing..."
    }
    
    # Start processing in a separate thread
    thread = threading.Thread(
        target=process_video_job,
        args=(prediction_id, model_id, data),
        daemon=True
    )
    thread.start()
    
    return {
        'id': prediction_id,
        'status': 'pending'
    }

@app.route('/outputs/<model_id>/<prediction_id>', methods=['GET'])
def get_output(model_id, prediction_id):
    if prediction_id not in video_jobs:
        return jsonify({"error": "Video job not found"}), 404
    
    job = video_jobs[prediction_id]
    
    if job['status'] != 'succeeded':
        return jsonify({"error": f"Video job status is {job['status']}, not succeeded"}), 400
    
    if 'output_path' not in job:
        return jsonify({"error": "Video output path not found"}), 404
    
    filename = os.path.basename(job['output_path'])
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/status/<model_id>/<prediction_id>', methods=['GET'])
@json_response
def get_status(model_id, prediction_id):
    if prediction_id not in video_jobs:
        return {"error": "Video job not found"}, 404
    
    job = video_jobs[prediction_id]
    
    # Build a complete status response with all available information
    response = {
        'id': prediction_id,
        'status': job['status'],
        'logs': job.get('logs', ''),
        'created_at': job['created_at'],
        'updated_at': job['updated_at'],
        'progress': job.get('progress', 0),  # Include progress percentage
    }
    
    # If there's a video URL available, include it
    if job['status'] == 'succeeded' and 'output_path' in job:
        filename = os.path.basename(job['output_path'])
        response['video_url'] = f"/outputs/{model_id}/{prediction_id}"
    
    # If this is a Replicate job, include the Replicate ID
    if 'replicate_id' in job:
        response['replicate_id'] = job['replicate_id']
    
    return response

@app.route('/outputs', methods=['GET'])
@json_response
def list_outputs():
    successful_jobs = [
        {
            'id': job_id,
            'status': job_data['status'],
            'model_id': job_data['model_id'],
            'created_at': job_data['created_at']
        }
        for job_id, job_data in video_jobs.items()
        if job_data['status'] == 'succeeded'
    ]
    return successful_jobs

@app.route('/', methods=['GET'])
@json_response
def health_check():
    return {"status": "healthy"}

# Video health check endpoint
@app.route('/video/health')
def video_health_check():
    try:
        # Basic health check
        return jsonify({
            "status": "healthy",
            "gpu_available": False,  # Default to false for simple implementation
            "service": "Video Generation API (Flask)"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "service": "Video Generation API (Flask)"
        })

# Serve static files from output directory
@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(output_dir, filename)

# A catch-all route for direct video file requests
@app.route('/<path:video_id>')
def redirect_video_files(video_id):
    # Check if this looks like a video file request (hunyuan_ID/filename.mp4)
    video_pattern = r'^(hunyuan_[a-zA-Z0-9_]+)(/.+)?$'
    match = re.match(video_pattern, video_id)
    
    if match:
        # This is a video ID request, redirect to the proper path
        video_id_part = match.group(1)
        file_part = match.group(2) or "/generated_video.mp4"  # Default to generated_video.mp4 if not specified
        
        # Check which directory exists
        output_path = output_dir / video_id_part
        outputs_path = outputs_dir / video_id_part
        
        if output_path.exists():
            # Redirect to /output/path
            return redirect(f"/output/{video_id_part}{file_part}")
        elif outputs_path.exists():
            # Redirect to /outputs/path
            return redirect(f"/outputs/{video_id_part}{file_part}")
    
    # Not a video request or video doesn't exist
    return jsonify({
        "error": "Not Found", 
        "message": f"Resource not found: {video_id}",
        "documentation": "/docs"
    }), 404

if __name__ == '__main__':
    print(f"Starting Flask server on http://0.0.0.0:8000")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    app.run(host='0.0.0.0', port=8000, debug=True) 
import os
import argparse
import torch
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
import uuid
import time
import subprocess
from pathlib import Path
import threading

# Load environment variables
load_dotenv()

# Get the model path from environment variable or use default
MODEL_PATH = os.getenv("HUNYUANVIDEO_MODEL_PATH", "/root/.cache/huggingface/hub")
RESULTS_DIR = os.getenv("RESULTS_DIR", "./results")
os.makedirs(RESULTS_DIR, exist_ok=True)

app = Flask(__name__)

# Store in-progress generations
active_generations = {}

@app.route('/generate', methods=['POST'])
def generate_video():
    data = request.json
    
    # Validate input
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing prompt in request"}), 400
    
    # Extract parameters with defaults
    prompt = data['prompt']
    width = data.get('width', 1280)
    height = data.get('height', 720)
    video_length = data.get('video_length', 129)
    steps = data.get('steps', 50)
    seed = data.get('seed', int(time.time()))
    embedded_cfg_scale = data.get('embedded_cfg_scale', 6.0)
    flow_shift = data.get('flow_shift', 7.0)
    flow_reverse = data.get('flow_reverse', True)
    
    generation_id = str(uuid.uuid4())
    
    # Initialize with pending status
    active_generations[generation_id] = {
        "id": generation_id,
        "status": "pending",
        "video_path": None,
        "error": None
    }
    
    # Start generation in background
    thread = threading.Thread(
        target=run_video_generation,
        args=(
            generation_id,
            prompt,
            width,
            height,
            video_length,
            steps,
            seed,
            embedded_cfg_scale,
            flow_shift,
            flow_reverse
        )
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "id": generation_id,
        "status": "pending"
    })

@app.route('/status/<generation_id>', methods=['GET'])
def get_status(generation_id):
    if generation_id not in active_generations:
        return jsonify({"error": "Generation ID not found"}), 404
    
    return jsonify(active_generations[generation_id])

@app.route('/video/<generation_id>', methods=['GET'])
def get_video(generation_id):
    if generation_id not in active_generations:
        return jsonify({"error": "Generation ID not found"}), 404
    
    generation = active_generations[generation_id]
    
    if generation["status"] != "completed":
        return jsonify({"error": f"Video generation is {generation['status']}"}), 400
    
    if not os.path.exists(generation["video_path"]):
        return jsonify({"error": "Video file not found"}), 404
    
    return send_file(generation["video_path"], mimetype='video/mp4')

def run_video_generation(
    generation_id,
    prompt,
    width,
    height,
    video_length,
    steps,
    seed,
    embedded_cfg_scale,
    flow_shift,
    flow_reverse
):
    try:
        active_generations[generation_id]["status"] = "running"
        
        output_path = os.path.join(RESULTS_DIR, f"{generation_id}.mp4")
        
        # Build command
        cmd = [
            "python3", "sample_video.py",
            "--video-size", str(width), str(height),
            "--video-length", str(video_length),
            "--infer-steps", str(steps),
            "--prompt", prompt,
            "--seed", str(seed),
            "--embedded-cfg-scale", str(embedded_cfg_scale),
            "--flow-shift", str(flow_shift),
            "--save-path", output_path
        ]
        
        if flow_reverse:
            cmd.append("--flow-reverse")
        
        # Run the command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Video generation failed: {stderr}")
        
        active_generations[generation_id]["status"] = "completed"
        active_generations[generation_id]["video_path"] = output_path
    
    except Exception as e:
        active_generations[generation_id]["status"] = "failed"
        active_generations[generation_id]["error"] = str(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run HunyuanVideo API server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    
    print(f"Starting HunyuanVideo Flask API server on {args.host}:{args.port}")
    print(f"Using model path: {MODEL_PATH}")
    print(f"Results directory: {RESULTS_DIR}")
    
    app.run(host=args.host, port=args.port, debug=args.debug) 
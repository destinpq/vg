#!/usr/bin/env python3
import os
import time
import uuid
import json
import logging
import datetime
import threading
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template_string
import torch
from optimized_hunyuan_generator import (
    optimize_cuda_settings, 
    run_video_generation, 
    get_gpu_memory_info, 
    clear_gpu_memory
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HunyuanVideo-API")

# Configure paths
MODEL_PATH = os.getenv("HUNYUANVIDEO_MODEL_PATH", "/root/.cache/huggingface/hub")
RESULTS_DIR = os.getenv("RESULTS_DIR", "./results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Configure FP8 weights path
FP8_WEIGHTS_PATH = os.getenv("FP8_WEIGHTS_PATH", None)

# Apply CUDA optimizations for H100
optimize_cuda_settings()

app = Flask(__name__)

# Store in-progress generations
active_generations = {}

# Store statistics for reporting
stats = {
    "total_requests": 0,
    "completed_requests": 0,
    "failed_requests": 0,
    "total_generation_time": 0,
    "average_generation_time": 0,
    "resolutions": {},
    "daily_stats": {},
    "hourly_stats": {},
}

# Simple queue for load balancing
request_queue = []
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "1"))
queue_lock = threading.Lock()
queue_processor_running = False

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>HunyuanVideo Generator</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        form {
            background: #f9f9f9;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 8px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        input[type="checkbox"] {
            width: auto;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #45a049;
        }
        .status-container {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            display: none;
        }
        .video-container {
            margin-top: 20px;
            display: none;
        }
        video {
            max-width: 100%;
            height: auto;
        }
        #status {
            font-weight: bold;
        }
        .hidden {
            display: none;
        }
        .queue-info {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>HunyuanVideo Generator</h1>
    
    <div id="queueInfo" class="queue-info">
        <p>Current queue status: <span id="queueStatus">Checking...</span></p>
    </div>
    
    <form id="generationForm">
        <div>
            <label for="prompt">Text Prompt:</label>
            <input type="text" id="prompt" name="prompt" required placeholder="A cat walks on the grass, realistic style.">
        </div>
        
        <div>
            <label for="resolution">Resolution:</label>
            <select id="resolution" name="resolution">
                <option value="1920x1080">1920x1080 (Full HD) - High Quality</option>
                <option value="1280x720" selected>1280x720 (HD) - Good Balance</option>
                <option value="960x544">960x544 (SD) - Faster</option>
                <option value="720x720">720x720 (Square) - Faster</option>
            </select>
        </div>
        
        <div>
            <label for="steps">Inference Steps:</label>
            <select id="steps" name="steps">
                <option value="50">50 - Highest Quality</option>
                <option value="40" selected>40 - Good Balance</option>
                <option value="30">30 - Faster</option>
            </select>
        </div>
        
        <div>
            <label for="seed">Random Seed (optional):</label>
            <input type="number" id="seed" name="seed" placeholder="Leave blank for random">
        </div>
        
        <div>
            <label for="embedded_cfg_scale">Guidance Scale:</label>
            <input type="number" id="embedded_cfg_scale" name="embedded_cfg_scale" value="6.0" step="0.5" min="1" max="15">
        </div>
        
        <div>
            <label>
                <input type="checkbox" id="use_fp8" name="use_fp8" checked>
                Use FP8 (Memory Efficient)
            </label>
        </div>
        
        <button type="submit" id="generateBtn">Generate Video</button>
    </form>
    
    <div id="statusContainer" class="status-container">
        <h3>Generation Status</h3>
        <p>ID: <span id="generationId"></span></p>
        <p>Status: <span id="status">Pending</span></p>
        <p>Queue Position: <span id="queuePosition">-</span></p>
        <div id="errorContainer" class="hidden">
            <p>Error: <span id="errorMessage"></span></p>
        </div>
    </div>
    
    <div id="videoContainer" class="video-container">
        <h3>Generated Video</h3>
        <video id="videoPlayer" controls></video>
        <p>
            <a id="downloadLink" href="#" download>Download Video</a>
        </p>
    </div>
    
    <script>
        // Update queue status periodically
        function updateQueueStatus() {
            fetch('/api/queue-status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('queueStatus').textContent = 
                        `${data.active_jobs} active, ${data.queued_jobs} in queue`;
                    setTimeout(updateQueueStatus, 5000);
                })
                .catch(error => {
                    console.error('Error fetching queue status:', error);
                    setTimeout(updateQueueStatus, 10000);
                });
        }
        
        // Start queue status updates
        updateQueueStatus();
        
        document.getElementById('generationForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const statusContainer = document.getElementById('statusContainer');
            const videoContainer = document.getElementById('videoContainer');
            const errorContainer = document.getElementById('errorContainer');
            
            statusContainer.style.display = 'block';
            videoContainer.style.display = 'none';
            errorContainer.classList.add('hidden');
            
            document.getElementById('status').textContent = 'Pending';
            document.getElementById('generateBtn').disabled = true;
            
            // Get form values
            const prompt = document.getElementById('prompt').value;
            const resolution = document.getElementById('resolution').value;
            const [width, height] = resolution.split('x').map(Number);
            const steps = parseInt(document.getElementById('steps').value);
            const seedInput = document.getElementById('seed').value;
            const seed = seedInput ? parseInt(seedInput) : null;
            const embedded_cfg_scale = parseFloat(document.getElementById('embedded_cfg_scale').value);
            const use_fp8 = document.getElementById('use_fp8').checked;
            
            // Create request body
            const requestBody = {
                prompt,
                width,
                height,
                steps,
                embedded_cfg_scale,
                use_fp8
            };
            
            if (seed !== null) {
                requestBody.seed = seed;
            }
            
            try {
                // Send generation request
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'Failed to start generation');
                }
                
                const generationId = data.id;
                document.getElementById('generationId').textContent = generationId;
                if (data.queue_position !== undefined) {
                    document.getElementById('queuePosition').textContent = data.queue_position;
                }
                
                // Poll for status updates
                const checkStatus = async () => {
                    try {
                        const statusResponse = await fetch(`/api/status/${generationId}`);
                        const statusData = await statusResponse.json();
                        
                        document.getElementById('status').textContent = statusData.status;
                        if (statusData.queue_position !== undefined) {
                            document.getElementById('queuePosition').textContent = statusData.queue_position;
                        }
                        
                        if (statusData.status === 'failed') {
                            errorContainer.classList.remove('hidden');
                            document.getElementById('errorMessage').textContent = statusData.error || 'Unknown error';
                            document.getElementById('generateBtn').disabled = false;
                            return;
                        }
                        
                        if (statusData.status === 'completed') {
                            // Show video
                            videoContainer.style.display = 'block';
                            const videoPlayer = document.getElementById('videoPlayer');
                            const downloadLink = document.getElementById('downloadLink');
                            
                            videoPlayer.src = `/api/video/${generationId}`;
                            downloadLink.href = `/api/video/${generationId}`;
                            downloadLink.download = `hunyuan_video_${generationId}.mp4`;
                            
                            document.getElementById('generateBtn').disabled = false;
                            return;
                        }
                        
                        // Keep polling if still in progress
                        setTimeout(checkStatus, 2000);
                    } catch (error) {
                        console.error('Error checking status:', error);
                        document.getElementById('status').textContent = 'Error checking status';
                        document.getElementById('generateBtn').disabled = false;
                    }
                };
                
                checkStatus();
                
            } catch (error) {
                console.error('Error submitting generation:', error);
                document.getElementById('status').textContent = 'Error';
                errorContainer.classList.remove('hidden');
                document.getElementById('errorMessage').textContent = error.message;
                document.getElementById('generateBtn').disabled = false;
            }
        });
    </script>
</body>
</html>
"""

def update_stats(generation_info):
    """Update statistics for reporting"""
    with queue_lock:
        # Update total stats
        stats["total_requests"] += 1
        
        if generation_info.get("status") == "completed":
            stats["completed_requests"] += 1
            
            # Track generation time if available
            if "generation_time" in generation_info:
                gen_time = generation_info["generation_time"]
                stats["total_generation_time"] += gen_time
                stats["average_generation_time"] = stats["total_generation_time"] / stats["completed_requests"]
            
            # Track resolution stats
            resolution = f"{generation_info.get('width', 0)}x{generation_info.get('height', 0)}"
            if resolution in stats["resolutions"]:
                stats["resolutions"][resolution] += 1
            else:
                stats["resolutions"][resolution] = 1
                
        elif generation_info.get("status") == "failed":
            stats["failed_requests"] += 1
            
        # Update daily stats
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today not in stats["daily_stats"]:
            stats["daily_stats"][today] = {
                "total": 0,
                "completed": 0,
                "failed": 0
            }
        
        stats["daily_stats"][today]["total"] += 1
        if generation_info.get("status") == "completed":
            stats["daily_stats"][today]["completed"] += 1
        elif generation_info.get("status") == "failed":
            stats["daily_stats"][today]["failed"] += 1
            
        # Update hourly stats
        hour = datetime.datetime.now().strftime("%Y-%m-%d %H:00")
        if hour not in stats["hourly_stats"]:
            stats["hourly_stats"][hour] = {
                "total": 0,
                "completed": 0,
                "failed": 0
            }
        
        stats["hourly_stats"][hour]["total"] += 1
        if generation_info.get("status") == "completed":
            stats["hourly_stats"][hour]["completed"] += 1
        elif generation_info.get("status") == "failed":
            stats["hourly_stats"][hour]["failed"] += 1

def process_queue():
    """Process the queue of video generation requests"""
    global queue_processor_running
    
    with queue_lock:
        if queue_processor_running:
            return
        queue_processor_running = True
    
    try:
        while True:
            current_jobs = 0
            next_job = None
            
            with queue_lock:
                # Count current active jobs
                current_jobs = len([g for g in active_generations.values() 
                                  if g["status"] in ["running"]])
                
                # Check if we can process more jobs
                if current_jobs < MAX_CONCURRENT_JOBS and request_queue:
                    next_job = request_queue.pop(0)
                    
                    # Update queue positions for remaining items
                    for i, job_id in enumerate(request_queue):
                        if job_id in active_generations:
                            active_generations[job_id]["queue_position"] = i + 1
                
                # If no jobs to process or at capacity, exit
                if next_job is None:
                    queue_processor_running = False
                    break
            
            # Process the next job if we have one
            if next_job and next_job in active_generations:
                job = active_generations[next_job]
                _run_generation(
                    job["id"],
                    job["prompt"],
                    job["video_path"],
                    job["width"],
                    job["height"],
                    job["video_length"],
                    job["steps"],
                    job["seed"],
                    job["embedded_cfg_scale"],
                    job["flow_shift"],
                    job["flow_reverse"],
                    job["use_fp8"],
                )
            
            # Small delay before checking again
            time.sleep(0.5)
    except Exception as e:
        logger.error(f"Error in queue processor: {str(e)}")
    finally:
        with queue_lock:
            queue_processor_running = False

@app.route('/')
def index():
    """Render the web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """API endpoint to generate a video"""
    try:
        data = request.json
        
        # Validate input
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing prompt in request"}), 400
        
        # Extract parameters with defaults
        prompt = data['prompt']
        width = data.get('width', 1280)
        height = data.get('height', 720)
        video_length = data.get('video_length', 129)  # HunyuanVideo default
        steps = data.get('steps', 50)
        seed = data.get('seed', None)
        embedded_cfg_scale = data.get('embedded_cfg_scale', 6.0)
        flow_shift = data.get('flow_shift', 7.0)
        flow_reverse = data.get('flow_reverse', True)
        use_fp8 = data.get('use_fp8', True)
        
        # Check if resolution is supported
        supported_resolutions = [
            (1920, 1080), # Full HD
            (1280, 720),  # HD
            (960, 544),   # SD
            (720, 720)    # Square
        ]
        
        if (width, height) not in supported_resolutions:
            return jsonify({
                "error": f"Unsupported resolution: {width}x{height}. Please use one of the supported resolutions."
            }), 400
        
        # Create a unique ID for this generation
        generation_id = str(uuid.uuid4())
        
        # Create unique output path
        output_path = os.path.join(RESULTS_DIR, f"{generation_id}.mp4")
        
        # Get queue position
        with queue_lock:
            queue_position = len(request_queue)
            request_queue.append(generation_id)
            
            # Initialize with pending status
            active_generations[generation_id] = {
                "id": generation_id,
                "status": "queued",
                "queue_position": queue_position,
                "prompt": prompt,
                "video_path": output_path,
                "width": width,
                "height": height,
                "video_length": video_length,
                "steps": steps,
                "seed": seed,
                "embedded_cfg_scale": embedded_cfg_scale,
                "flow_shift": flow_shift,
                "flow_reverse": flow_reverse,
                "use_fp8": use_fp8,
                "error": None,
                "created_at": datetime.datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
                "generation_time": None
            }
            
            # Update stats
            update_stats(active_generations[generation_id])
        
        # Start queue processor if not running
        threading.Thread(target=process_queue, daemon=True).start()
        
        return jsonify({
            "id": generation_id,
            "status": "queued",
            "queue_position": queue_position
        })
        
    except Exception as e:
        logger.error(f"Error starting generation: {str(e)}")
        return jsonify({"error": str(e)}), 500

def _run_generation(
    generation_id,
    prompt,
    output_path,
    width,
    height,
    video_length,
    steps,
    seed,
    embedded_cfg_scale,
    flow_shift,
    flow_reverse,
    use_fp8,
):
    """Run the video generation for a queued request"""
    try:
        # Update status to running
        start_time = time.time()
        active_generations[generation_id]["status"] = "running"
        active_generations[generation_id]["started_at"] = datetime.datetime.now().isoformat()
        active_generations[generation_id]["queue_position"] = 0
        
        # Run the generation
        run_video_generation(
            prompt=prompt,
            output_path=output_path,
            width=width,
            height=height,
            video_length=video_length,
            steps=steps,
            seed=seed,
            embedded_cfg_scale=embedded_cfg_scale,
            flow_shift=flow_shift,
            flow_reverse=flow_reverse,
            use_fp8=use_fp8,
            fp8_weights_path=FP8_WEIGHTS_PATH
        )
        
        # Calculate generation time
        generation_time = time.time() - start_time
        
        # Update status to completed
        active_generations[generation_id]["status"] = "completed"
        active_generations[generation_id]["completed_at"] = datetime.datetime.now().isoformat()
        active_generations[generation_id]["generation_time"] = generation_time
        
        # Update stats
        update_stats(active_generations[generation_id])
        
    except Exception as e:
        logger.error(f"Error in generation {generation_id}: {str(e)}")
        active_generations[generation_id]["status"] = "failed"
        active_generations[generation_id]["error"] = str(e)
        active_generations[generation_id]["completed_at"] = datetime.datetime.now().isoformat()
        
        # Update stats
        update_stats(active_generations[generation_id])
        
        # Make sure to clean up memory on error
        clear_gpu_memory()
    
    # Re-run queue processor to pick up the next job
    threading.Thread(target=process_queue, daemon=True).start()

@app.route('/api/status/<generation_id>', methods=['GET'])
def get_status(generation_id):
    """Get the status of a generation"""
    if generation_id not in active_generations:
        return jsonify({"error": "Generation ID not found"}), 404
    
    return jsonify(active_generations[generation_id])

@app.route('/api/video/<generation_id>', methods=['GET'])
def get_video(generation_id):
    """Get the generated video"""
    if generation_id not in active_generations:
        return jsonify({"error": "Generation ID not found"}), 404
    
    generation = active_generations[generation_id]
    
    if generation["status"] != "completed":
        return jsonify({"error": f"Video generation is {generation['status']}"}), 400
    
    if not os.path.exists(generation["video_path"]):
        return jsonify({"error": "Video file not found"}), 404
    
    return send_file(generation["video_path"], mimetype='video/mp4')

@app.route('/api/queue-status', methods=['GET'])
def queue_status():
    """Get the current queue status"""
    with queue_lock:
        active_jobs = len([g for g in active_generations.values() if g["status"] == "running"])
        queued_jobs = len(request_queue)
        
    return jsonify({
        "active_jobs": active_jobs,
        "queued_jobs": queued_jobs,
        "max_concurrent_jobs": MAX_CONCURRENT_JOBS
    })

@app.route('/api/gpu-status', methods=['GET'])
def gpu_status():
    """Get GPU status information"""
    try:
        return jsonify({
            "gpu_info": get_gpu_memory_info(),
            "active_generations": len([g for g in active_generations.values() if g["status"] == "running"]),
            "queued_generations": len(request_queue),
            "completed_generations": len([g for g in active_generations.values() if g["status"] == "completed"])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get generation statistics"""
    return jsonify(stats)

@app.route('/api/clean-old-videos', methods=['POST'])
def clean_old_videos():
    """Clean up old generated videos to free up disk space"""
    try:
        max_age_hours = request.json.get('max_age_hours', 24)
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        
        # Find videos older than the specified age
        deleted_count = 0
        preserved_count = 0
        
        for file in os.listdir(RESULTS_DIR):
            if file.endswith('.mp4'):
                file_path = os.path.join(RESULTS_DIR, file)
                file_age = current_time - os.path.getmtime(file_path)
                
                if file_age > max_age_seconds:
                    # Check if it's safe to delete (not in use)
                    file_id = os.path.splitext(file)[0]
                    is_active = False
                    
                    for gen in active_generations.values():
                        if gen["status"] == "running" and gen["video_path"] == file_path:
                            is_active = True
                            break
                    
                    if not is_active:
                        os.remove(file_path)
                        deleted_count += 1
                else:
                    preserved_count += 1
        
        return jsonify({
            "success": True,
            "deleted_count": deleted_count,
            "preserved_count": preserved_count,
            "max_age_hours": max_age_hours
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="HunyuanVideo Flask API Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--max-concurrent-jobs", type=int, help="Maximum number of concurrent generation jobs")
    
    args = parser.parse_args()
    
    # Set max concurrent jobs from args if provided
    if args.max_concurrent_jobs:
        MAX_CONCURRENT_JOBS = args.max_concurrent_jobs
    
    # Print API URL
    logger.info(f"Starting HunyuanVideo Flask API server on http://{args.host}:{args.port}")
    logger.info(f"Web interface available at http://{args.host}:{args.port}/")
    logger.info(f"Maximum concurrent jobs: {MAX_CONCURRENT_JOBS}")
    
    # Start Flask app
    app.run(host=args.host, port=args.port, debug=args.debug) 
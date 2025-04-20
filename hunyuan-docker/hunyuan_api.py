#!/usr/bin/env python3
"""
Flask API server for Tencent Hunyuan Video model running on H100 GPU
"""
import os
import time
import torch
import base64
import logging
import argparse
import numpy as np
import sys
from io import BytesIO
from pathlib import Path
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add the HunyuanVideo directory to the Python path
sys.path.append("/root/hunyuan-models/HunyuanVideo")

# Import Hunyuan Video pipeline
try:
    from hyvideo.pipelines.hunyuan_video_pipeline import HunyuanVideoPipeline
except ImportError as e:
    print(f"Error importing HunyuanVideoPipeline: {e}")
    print("Is the HunyuanVideo repository properly installed?")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Model configuration
MODEL_DIR = "/root/hunyuan-models/HunyuanVideo/ckpts"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
OUTPUT_DIR = "/root/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize pipeline
pipe = None

def initialize_model(use_cpu_offload=False, flow_reverse=True):
    """Initialize the Hunyuan Video model"""
    global pipe
    logger.info(f"Loading Hunyuan Video model from {MODEL_DIR} on {DEVICE}")
    
    try:
        # Print out available CUDA devices
        if torch.cuda.is_available():
            logger.info(f"CUDA device count: {torch.cuda.device_count()}")
            logger.info(f"Current CUDA device: {torch.cuda.current_device()}")
            logger.info(f"CUDA device name: {torch.cuda.get_device_name(0)}")
        
        # Load the model
        pipe = HunyuanVideoPipeline.from_pretrained(
            MODEL_DIR,
            device_map="auto" if use_cpu_offload else DEVICE,
            torch_dtype=torch.float16,
        )
        
        # Configure flow direction
        pipe.scheduler.flow_reverse = flow_reverse
        logger.info(f"Flow reverse mode: {flow_reverse}")
        
        if use_cpu_offload and DEVICE == "cuda":
            logger.info("Enabling CPU offload for model")
            pipe.enable_model_cpu_offload()
        else:
            logger.info(f"No CPU offload, using device: {DEVICE}")
        
        logger.info("Model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    gpu_info = None
    if torch.cuda.is_available():
        gpu_info = {
            "name": torch.cuda.get_device_name(0),
            "memory_allocated_gb": round(torch.cuda.memory_allocated(0) / (1024**3), 2),
            "memory_reserved_gb": round(torch.cuda.memory_reserved(0) / (1024**3), 2),
            "total_memory_gb": round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2),
        }
    
    return jsonify({
        "status": "healthy",
        "model_loaded": pipe is not None,
        "gpu_available": torch.cuda.is_available(),
        "gpu_info": gpu_info,
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_path": MODEL_DIR,
        "output_path": OUTPUT_DIR
    })

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """Generate video from text prompt."""
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Get optional parameters
        width = int(data.get('width', 576))
        height = int(data.get('height', 320))
        num_inference_steps = int(data.get('num_inference_steps', 50))
        video_length = int(data.get('video_length', 129))  # Default from the repo
        embedded_cfg_scale = float(data.get('embedded_cfg_scale', 6.0))
        seed = data.get('seed')
        output_format = data.get('output_format', "gif")
        
        # Apply reasonable limits to prevent OOM
        if width * height > 1280 * 720:
            logger.warning(f"Requested resolution {width}x{height} exceeds limits, using 720p")
            width, height = 1280, 720
            
        if num_inference_steps > 100:
            logger.warning(f"Requested steps {num_inference_steps} exceeds limits, using 100")
            num_inference_steps = 100
            
        if video_length > 200:
            logger.warning(f"Requested length {video_length} exceeds limits, using 200")
            video_length = 200
        
        # Set seed if provided
        if seed is not None:
            generator = torch.Generator(device=DEVICE).manual_seed(int(seed))
        else:
            # Random seed for reproducibility
            seed = np.random.randint(0, 2147483647)
            generator = torch.Generator(device=DEVICE).manual_seed(seed)
        
        logger.info(f"Generating video for prompt: '{prompt}'")
        logger.info(f"Parameters: width={width}, height={height}, steps={num_inference_steps}, length={video_length}, seed={seed}")
        
        # Generate a unique ID for output
        timestamp = int(time.time())
        output_id = f"hunyuan_{timestamp}"
        output_dir = os.path.join(OUTPUT_DIR, output_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate the video
        start_time = time.time()
        
        with torch.inference_mode():
            video_frames = pipe(
                prompt=prompt,
                video_length=video_length,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                embedded_cfg_scale=embedded_cfg_scale,
                generator=generator,
            ).frames
        
        # Save the video
        output_file = os.path.join(output_dir, f"generated_video.{output_format}")
        logger.info(f"Saving video to {output_file}")
        
        # Convert frames to PIL images
        pil_frames = [Image.fromarray(frame) for frame in video_frames]
        
        # Save as GIF or MP4
        if output_format == "gif":
            pil_frames[0].save(
                output_file,
                save_all=True,
                append_images=pil_frames[1:],
                duration=100,  # milliseconds per frame
                loop=0,
            )
        else:
            # For other formats, save as MP4 (requires additional libraries)
            try:
                import imageio
                imageio.mimsave(output_file, video_frames, fps=24)
            except ImportError:
                # Fall back to GIF if imageio is not available
                output_file = os.path.join(output_dir, "generated_video.gif")
                pil_frames[0].save(
                    output_file,
                    save_all=True,
                    append_images=pil_frames[1:],
                    duration=100,
                    loop=0,
                )
        
        # Encode as base64 for direct transmission
        with open(output_file, "rb") as f:
            video_bytes = f.read()
        
        video_b64 = base64.b64encode(video_bytes).decode('utf-8')
        
        generation_time = time.time() - start_time
        
        # Get relative output path for web access
        output_path = os.path.join(output_id, os.path.basename(output_file))
        
        return jsonify({
            "success": True,
            "prompt": prompt,
            "video_path": output_file,
            "web_path": output_path,
            "video_base64": video_b64,
            "generation_time_seconds": generation_time,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": num_inference_steps,
                "video_length": video_length,
                "embedded_cfg_scale": embedded_cfg_scale,
                "seed": seed
            }
        })
    
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description='Run Hunyuan Video API server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind')
    parser.add_argument('--use-cpu-offload', action='store_true', help='Enable CPU offloading to save GPU memory')
    parser.add_argument('--flow-reverse', action='store_true', help='Use reverse flow matching')
    args = parser.parse_args()
    
    # Initialize the model
    if initialize_model(args.use_cpu_offload, args.flow_reverse):
        # Start the Flask server
        logger.info(f"Starting Flask server on {args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=False)
    else:
        logger.error("Failed to initialize model. Exiting.")
        sys.exit(1) 
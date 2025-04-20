#!/bin/bash
# Script to set up Tencent Hunyuan model on H100 GPU droplet

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_DIR="/root"
MODEL_DIR="$BASE_DIR/hunyuan-models"
VENV_DIR="$BASE_DIR/hunyuan-venv"
REPO_DIR="$MODEL_DIR/HunyuanVideo"
CKPTS_DIR="$REPO_DIR/ckpts"
HF_TOKEN="" # Add your Hugging Face token if the model is gated

echo -e "${GREEN}=== Setting up Tencent Hunyuan Video Model on H100 GPU ===${NC}"

# Install system dependencies
echo -e "${BLUE}Installing system dependencies...${NC}"
apt-get update && apt-get install -y \
    python3-pip python3-dev python3-venv \
    git wget curl \
    libgl1-mesa-glx ffmpeg \
    && apt-get clean

# Create model directory
echo -e "${BLUE}Creating model directory...${NC}"
mkdir -p $MODEL_DIR
mkdir -p $CKPTS_DIR

# Check NVIDIA GPU
echo -e "${BLUE}Checking NVIDIA GPU...${NC}"
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}NVIDIA drivers not found. Please install NVIDIA drivers first.${NC}"
    exit 1
fi

nvidia-smi
CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
echo -e "${GREEN}CUDA Version: $CUDA_VERSION${NC}"

# Create and activate virtual environment
echo -e "${BLUE}Setting up Python virtual environment...${NC}"
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip setuptools wheel
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
pip install flask flask-cors safetensors huggingface_hub

# Clone HunyuanVideo repository
echo -e "${BLUE}Cloning HunyuanVideo repository...${NC}"
git clone https://github.com/zsxkib/HunyuanVideo.git $REPO_DIR
cd $REPO_DIR

# Install the repository requirements
echo -e "${BLUE}Installing HunyuanVideo requirements...${NC}"
pip install -e .

# Set up HF token if provided
if [ ! -z "$HF_TOKEN" ]; then
    echo -e "${BLUE}Setting up Hugging Face token...${NC}"
    huggingface-cli login --token $HF_TOKEN
fi

# Download model weights
echo -e "${BLUE}Downloading model weights...${NC}"
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='Tencent/hunyuan-2-video',
    local_dir='./ckpts',
    local_dir_use_symlinks=False,
    token='$HF_TOKEN'
)
"

# Create a Flask API wrapper for the model
echo -e "${BLUE}Creating Flask API for Hunyuan...${NC}"
cat > $MODEL_DIR/hunyuan_api.py << 'EOF'
#!/usr/bin/env python3
"""
Flask API server for Tencent Hunyuan model running on H100 GPU
"""
import os
import time
import torch
import base64
import logging
import argparse
import numpy as np
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

# Add the Hunyuan repository to path
sys.path.append("/root/hunyuan-models/HunyuanVideo")
from hyvideo.pipelines.hunyuan_video_pipeline import HunyuanVideoPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Model configuration
MODEL_DIR = "/root/hunyuan-models/HunyuanVideo/ckpts"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_MEMORY = {0: "70GiB"}  # For H100 80GB, allocate 70GB

# Initialize pipeline
pipe = None

def initialize_model(use_cpu_offload=False, flow_reverse=True):
    global pipe
    logger.info(f"Loading Hunyuan model from {MODEL_DIR} on {DEVICE}")
    
    try:
        pipe = HunyuanVideoPipeline.from_pretrained(
            MODEL_DIR,
            device_map="auto" if use_cpu_offload else DEVICE,
            torch_dtype=torch.float16,
        )
        
        # Configure flow direction
        pipe.scheduler.flow_reverse = flow_reverse
        
        if use_cpu_offload and DEVICE == "cuda":
            pipe.enable_model_cpu_offload()
        
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
        width = data.get('width', 576)
        height = data.get('height', 320)
        num_inference_steps = data.get('num_inference_steps', 50)
        video_length = data.get('video_length', 129)  # Default from the repo
        flow_reverse = data.get('flow_reverse', True)
        embedded_cfg_scale = data.get('embedded_cfg_scale', 6.0)
        seed = data.get('seed')
        output_format = data.get('output_format', "gif")
        
        # Set seed if provided
        if seed is not None:
            generator = torch.Generator(device=DEVICE).manual_seed(seed)
        else:
            generator = None
        
        logger.info(f"Generating video for prompt: '{prompt}'")
        logger.info(f"Parameters: width={width}, height={height}, steps={num_inference_steps}, length={video_length}")
        
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
        video_path = f"/tmp/generated_video_{int(time.time())}.gif"
        
        # Convert frames to PIL images
        pil_frames = [Image.fromarray(frame) for frame in video_frames]
        
        # Save as GIF
        pil_frames[0].save(
            video_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=100,  # milliseconds per frame
            loop=0,
        )
        
        # Encode as base64 for direct transmission
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        
        video_b64 = base64.b64encode(video_bytes).decode('utf-8')
        
        generation_time = time.time() - start_time
        
        return jsonify({
            "success": True,
            "prompt": prompt,
            "video_path": video_path,
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
EOF

# Create a systemd service file for the API
echo -e "${BLUE}Creating systemd service for Hunyuan API...${NC}"
cat > /etc/systemd/system/hunyuan-api.service << EOF
[Unit]
Description=Hunyuan Video API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$MODEL_DIR
ExecStart=$VENV_DIR/bin/python $MODEL_DIR/hunyuan_api.py --use-cpu-offload --flow-reverse
Restart=on-failure
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=hunyuan-api
Environment="PYTHONPATH=$REPO_DIR"

[Install]
WantedBy=multi-user.target
EOF

# Create a startup script
echo -e "${BLUE}Creating startup script...${NC}"
cat > $MODEL_DIR/start-hunyuan-api.sh << EOF
#!/bin/bash
source $VENV_DIR/bin/activate
cd $MODEL_DIR
python hunyuan_api.py --use-cpu-offload --flow-reverse
EOF

chmod +x $MODEL_DIR/start-hunyuan-api.sh

# Enable and start the service
echo -e "${BLUE}Enabling and starting Hunyuan API service...${NC}"
systemctl daemon-reload
systemctl enable hunyuan-api.service
systemctl start hunyuan-api.service

# Check service status
echo -e "${BLUE}Checking service status...${NC}"
systemctl status hunyuan-api.service

echo -e "${GREEN}=== Hunyuan Video Model Setup Complete! ===${NC}"
echo -e "${YELLOW}The Hunyuan API is running at: http://localhost:8000${NC}"
echo -e "${YELLOW}Test endpoints:${NC}"
echo -e "  - Health check: curl http://localhost:8000/health"
echo -e "  - Generate video: curl -X POST -H 'Content-Type: application/json' -d '{\"prompt\":\"A cat playing piano\"}' http://localhost:8000/generate-video"
echo -e "\n${YELLOW}To restart the service:${NC} systemctl restart hunyuan-api.service"
echo -e "${YELLOW}To view logs:${NC} journalctl -u hunyuan-api.service -f" 
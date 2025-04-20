#!/bin/bash
set -e

echo "Setting up HunyuanVideo Docker environment..."

# Create directory if it doesn't exist
mkdir -p hunyuan-docker

# Create Dockerfile
cat > hunyuan-docker/Dockerfile << 'EOL'
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/root/hunyuan-models/HunyuanVideo
ENV FLOW_REVERSE=true
ENV USE_CPU_OFFLOAD=true
ENV HF_HOME=/root/hunyuan-models/huggingface
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip python3-dev python3-venv \
    git wget curl tmux \
    libsm6 libxext6 libxrender-dev libgl1-mesa-glx \
    ffmpeg ninja-build build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /root/hunyuan-models/HunyuanVideo/ckpts \
    && mkdir -p /root/hunyuan-models/huggingface \
    && mkdir -p /root/output

# Set up working directory
WORKDIR /root/hunyuan-models

# Create and activate virtual environment
RUN python3 -m venv /root/venv
ENV PATH="/root/venv/bin:$PATH"

# Upgrade pip and install base Python packages
RUN pip install --upgrade pip setuptools wheel && \
    pip install torch==2.1.0 torchvision==0.16.0 --extra-index-url https://download.pytorch.org/whl/cu121

# Clone HunyuanVideo repository
RUN git clone https://github.com/zsxkib/HunyuanVideo.git /root/hunyuan-models/HunyuanVideo

# Install HunyuanVideo dependencies
WORKDIR /root/hunyuan-models/HunyuanVideo
RUN pip install -e .

# Install additional dependencies
RUN pip install flask flask-cors requests tqdm huggingface_hub

# Copy API files
COPY hunyuan_api.py /root/hunyuan-models/
COPY download_weights.py /root/hunyuan-models/
COPY entrypoint.sh /root/hunyuan-models/

# Make scripts executable
RUN chmod +x /root/hunyuan-models/entrypoint.sh

# Expose port for API
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/root/hunyuan-models/entrypoint.sh"]
EOL

# Create download_weights.py
cat > hunyuan-docker/download_weights.py << 'EOL'
#!/usr/bin/env python3
"""
Script to download Hunyuan Video model weights from HuggingFace.
This script handles:
1. Authentication with HuggingFace (if token is provided)
2. Downloading the model weights
3. Verifying the downloaded files
"""
import os
import sys
import time
import argparse
import logging
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download, HfApi

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
MODEL_ID = "tencent/HunyuanVideo"
CHECKPOINTS_DIR = "/root/hunyuan-models/HunyuanVideo/ckpts"
REQUIRED_FILES = [
    "config.json",
    "model_index.json",
    "scheduler_config.json"
]

def setup_hf_auth(token):
    """Set up HuggingFace authentication"""
    if token:
        logger.info("Setting up HuggingFace authentication")
        os.environ["HUGGING_FACE_HUB_TOKEN"] = token
        api = HfApi(token=token)
        # Test authentication
        try:
            api.whoami()
            logger.info("Successfully authenticated with HuggingFace")
            return True
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    else:
        logger.info("No token provided, proceeding without authentication")
        return True

def download_weights(token=None):
    """Download the model weights from HuggingFace"""
    logger.info(f"Starting download of model weights for {MODEL_ID}")
    logger.info(f"Weights will be saved to {CHECKPOINTS_DIR}")
    
    # Ensure the checkpoints directory exists
    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
    
    # Set up authentication if token is provided
    if token and not setup_hf_auth(token):
        logger.error("Failed to authenticate with HuggingFace. Aborting download.")
        return False
    
    try:
        # Estimate size before downloading
        logger.info("Estimating download size (this may take a moment)...")
        try:
            # Try to estimate size (not always possible)
            api = HfApi(token=token if token else None)
            repo_info = api.repo_info(MODEL_ID)
            logger.info(f"Repository size: {repo_info.size_on_disk / (1024**3):.2f} GB")
        except Exception as e:
            logger.warning(f"Could not estimate repository size: {str(e)}")

        # Start download with progress
        logger.info(f"Downloading {MODEL_ID} to {CHECKPOINTS_DIR}...")
        start_time = time.time()
        
        # Use snapshot_download for the entire repository
        snapshot_download(
            repo_id=MODEL_ID,
            local_dir=CHECKPOINTS_DIR,
            local_dir_use_symlinks=False,
            token=token,
            resume_download=True,
            ignore_patterns=["*.md", "*.txt"]
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Download completed in {elapsed_time:.2f} seconds")
        
        # Verify downloaded files
        return verify_download()
        
    except Exception as e:
        logger.error(f"Error downloading weights: {str(e)}")
        return False

def verify_download():
    """Verify that all required files were downloaded"""
    logger.info("Verifying downloaded files...")
    
    # Check for required files
    missing_files = []
    for file in REQUIRED_FILES:
        file_path = os.path.join(CHECKPOINTS_DIR, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    # Count model files
    model_files = list(Path(CHECKPOINTS_DIR).glob("**/*.safetensors"))
    bin_files = list(Path(CHECKPOINTS_DIR).glob("**/*.bin"))
    
    logger.info(f"Found {len(model_files)} .safetensors files and {len(bin_files)} .bin files")
    
    total_size = sum(f.stat().st_size for f in model_files + bin_files) / (1024**3)
    logger.info(f"Total model size: {total_size:.2f} GB")
    
    # Assume success if we found any model files
    return len(model_files) > 0 or len(bin_files) > 0

def main():
    parser = argparse.ArgumentParser(description="Download Hunyuan Video model weights")
    parser.add_argument("--token", type=str, help="HuggingFace token for authentication")
    parser.add_argument("--model-id", type=str, default=MODEL_ID, help="HuggingFace model ID")
    parser.add_argument("--output-dir", type=str, default=CHECKPOINTS_DIR, help="Directory to save model weights")
    args = parser.parse_args()
    
    # Update globals if custom values provided
    global MODEL_ID, CHECKPOINTS_DIR
    MODEL_ID = args.model_id
    CHECKPOINTS_DIR = args.output_dir
    
    logger.info("Starting Hunyuan Video model weights download")
    logger.info(f"Model ID: {MODEL_ID}")
    logger.info(f"Output directory: {CHECKPOINTS_DIR}")
    
    success = download_weights(args.token)
    
    if success:
        logger.info("Model weights downloaded and verified successfully!")
        return 0
    else:
        logger.error("Failed to download or verify model weights.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOL

# Create entrypoint.sh
cat > hunyuan-docker/entrypoint.sh << 'EOL'
#!/bin/bash
set -e

# Configure colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Hunyuan Video API Server ===${NC}"

# Check NVIDIA GPU
echo -e "${BLUE}Checking NVIDIA GPU...${NC}"
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}NVIDIA drivers not found or not properly configured!${NC}"
    echo -e "${YELLOW}Running in CPU-only mode (not recommended)${NC}"
else
    nvidia-smi || echo -e "${YELLOW}Warning: nvidia-smi failed, but continuing...${NC}"
fi

# Download weights if not already present
CHECKPOINTS_DIR="/root/hunyuan-models/HunyuanVideo/ckpts"
echo -e "${BLUE}Checking for model weights in $CHECKPOINTS_DIR...${NC}"

# Check if we need to download weights
if [ -z "$(ls -A $CHECKPOINTS_DIR 2>/dev/null)" ]; then
    echo -e "${YELLOW}Model weights not found. Downloading...${NC}"
    
    # Check if HF_TOKEN is provided for private model repos
    if [ -n "$HF_TOKEN" ]; then
        echo -e "${BLUE}Using provided Hugging Face token for authentication.${NC}"
        python /root/hunyuan-models/download_weights.py --token "$HF_TOKEN"
    else
        echo -e "${BLUE}No HF_TOKEN provided. Attempting to download without authentication.${NC}"
        python /root/hunyuan-models/download_weights.py
    fi
else
    echo -e "${GREEN}Model weights found. Skipping download.${NC}"
    ls -lah $CHECKPOINTS_DIR
fi

# Get the number of model files
NUM_FILES=$(find "$CHECKPOINTS_DIR" -type f -name "*.bin" -o -name "*.safetensors" | wc -l)
echo -e "${BLUE}Found $NUM_FILES model files.${NC}"

# Check for essential model files
if [ $NUM_FILES -lt 3 ]; then
    echo -e "${YELLOW}Warning: Found fewer model files than expected. Some files may still be downloading.${NC}"
else
    echo -e "${GREEN}All model files appear to be present.${NC}"
fi

# Parse environment variables for API server
API_ARGS=""
if [ "$USE_CPU_OFFLOAD" = "true" ]; then
    API_ARGS="$API_ARGS --use-cpu-offload"
fi

if [ "$FLOW_REVERSE" = "true" ]; then
    API_ARGS="$API_ARGS --flow-reverse"
fi

# Start the API server
echo -e "${GREEN}Starting Hunyuan Video API Server...${NC}"
echo -e "${BLUE}API Args: $API_ARGS${NC}"
exec python /root/hunyuan-models/hunyuan_api.py $API_ARGS
EOL

# Create .dockerignore
cat > hunyuan-docker/.dockerignore << 'EOL'
# Ignore git
.git
.gitignore

# Ignore cache
__pycache__
*.pyc
*.pyo
*.pyd
.Python
.pytest_cache

# Do NOT ignore these specific files
!hunyuan_api.py
!download_weights.py
!entrypoint.sh
EOL

# Create docker-compose.yml
cat > docker-hunyuan-gpu.yml << 'EOL'
services:
  hunyuan-api:
    build:
      context: ./hunyuan-docker
      dockerfile: Dockerfile
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - hunyuan-weights:/root/hunyuan-models/HunyuanVideo/ckpts
      - ./output:/root/output
    environment:
      # You MUST provide a valid Hugging Face token with access to tencent/HunyuanVideo
      # Create one at https://huggingface.co/settings/tokens
      - HF_TOKEN=${HF_TOKEN:-default_token_for_testing}
      - USE_CPU_OFFLOAD=true
      - FLOW_REVERSE=true
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: [gpu]
              count: all
    healthcheck:
      test: ["CMD-SHELL", "curl -s -f http://localhost:8000/health > /dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

volumes:
  hunyuan-weights:
    driver: local
EOL

# Create dummy hunyuan_api.py if it doesn't exist
if [ ! -f hunyuan-docker/hunyuan_api.py ]; then
    echo "Creating placeholder hunyuan_api.py..."
    cat > hunyuan-docker/hunyuan_api.py << 'EOL'
#!/usr/bin/env python3
"""
HunyuanVideo API Server
This script sets up a Flask server to expose the HunyuanVideo model via a REST API.
"""
import os
import time
import argparse
import logging
from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import io
import json
import base64
import torch
import threading

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "hunyuan-video-api"})

@app.route('/generate', methods=['POST'])
def generate_video():
    """Generate a video from a text prompt"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Process with additional parameters
        width = data.get('width', 1280)
        height = data.get('height', 720)
        frames = data.get('frames', 129)
        steps = data.get('steps', 50)
        
        # For this placeholder, just return success
        return jsonify({
            "status": "success",
            "message": "This is a placeholder API. In the real version, this would generate a video.",
            "prompt": prompt,
            "parameters": {
                "width": width,
                "height": height,
                "frames": frames,
                "steps": steps
            }
        })
        
    except Exception as e:
        logger.error(f"Error in generate_video: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HunyuanVideo API Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--use-cpu-offload", action="store_true", help="Use CPU offload for the model")
    parser.add_argument("--flow-reverse", action="store_true", help="Use flow reverse for the model")
    args = parser.parse_args()
    
    logger.info("Starting HunyuanVideo API Server...")
    logger.info(f"Host: {args.host}, Port: {args.port}")
    
    # Print a notice if this is the dummy API
    logger.warning("THIS IS A PLACEHOLDER API. Replace with the actual implementation.")
    
    # Start the server
    app.run(host=args.host, port=args.port)
EOL
fi

echo "All files created successfully!"
echo "Now you can run:"
echo "  chmod +x hunyuan-docker/entrypoint.sh"
echo "  docker-compose -f docker-hunyuan-gpu.yml build"
echo "  docker-compose -f docker-hunyuan-gpu.yml up -d"
echo "Make sure to set your HF_TOKEN environment variable first:"
echo "  export HF_TOKEN=your_huggingface_token" 
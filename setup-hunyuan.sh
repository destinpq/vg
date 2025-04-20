#!/bin/bash
set -e

echo "Setting up Hunyuan for H100 GPU"
echo "=============================="

# Create output directory for model storage
mkdir -p output/hunyuan-models
echo "Created output directory for model storage"

# Check if HF_TOKEN is set
if [ -z "${HF_TOKEN}" ]; then
  echo "WARNING: HF_TOKEN environment variable is not set!"
  echo "You need a Hugging Face token with access to tencent/HunyuanVideo"
  echo "Create one at https://huggingface.co/settings/tokens"
  echo "Set it with: export HF_TOKEN=your_token_here"
  read -p "Would you like to continue without a token? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Create .env file for docker-compose
echo "Creating .env file with HF_TOKEN..."
echo "HF_TOKEN=${HF_TOKEN:-default_token_for_testing}" > .env

# Verify NVIDIA GPU is working
echo "Verifying NVIDIA GPU is available..."
if ! nvidia-smi > /dev/null 2>&1; then
  echo "ERROR: NVIDIA GPU not detected! Please run h100-fix.sh first and reboot."
  echo "If you've already done that, there might be issues with your NVIDIA driver installation."
  exit 1
fi

# Display GPU info
echo "GPU detected:"
nvidia-smi

# Create Docker configuration
echo "Creating Docker configuration..."
mkdir -p hunyuan-docker
cat > docker-hunyuan.yml << EOL
services:
  hunyuan-api:
    build:
      context: ./hunyuan-docker
      dockerfile: Dockerfile
    restart: always
    runtime: nvidia
    shm_size: '16gb'
    ulimits:
      memlock: -1
      stack: 67108864
    ports:
      - "8000:8000"
    volumes:
      - ./output:/root/output
    environment:
      - HF_TOKEN=\${HF_TOKEN:-default_token_for_testing}
      - USE_CPU_OFFLOAD=false
      - FLOW_REVERSE=true
      - MODEL_DIR=/root/output/hunyuan-models
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    healthcheck:
      test: ["CMD-SHELL", "curl -s -f http://localhost:8000/health > /dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
EOL

# Create Dockerfile
echo "Creating Dockerfile..."
cat > hunyuan-docker/Dockerfile << EOL
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/root/hunyuan-models/HunyuanVideo
ENV FLOW_REVERSE=true
ENV USE_CPU_OFFLOAD=false
ENV HF_HOME=/root/hunyuan-models/huggingface
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1
ENV MODEL_DIR=/root/output/hunyuan-models
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=all

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    python3-pip python3-dev python3-venv \\
    git wget curl tmux \\
    libsm6 libxext6 libxrender-dev libgl1-mesa-glx \\
    ffmpeg ninja-build build-essential \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /root/hunyuan-models/HunyuanVideo/ckpts \\
    && mkdir -p /root/hunyuan-models/huggingface \\
    && mkdir -p /root/output/hunyuan-models

# Set up working directory
WORKDIR /root/hunyuan-models

# Create and activate virtual environment
RUN python3 -m venv /root/venv
ENV PATH="/root/venv/bin:\$PATH"

# Upgrade pip and install base Python packages
RUN pip install --upgrade pip setuptools wheel && \\
    pip install torch==2.1.0 torchvision==0.16.0 --extra-index-url https://download.pytorch.org/whl/cu121

# Install optimized packages for H100
RUN pip install xformers==0.0.23

# Clone HunyuanVideo repository
RUN git clone https://github.com/Tencent/HunyuanVideo.git /root/hunyuan-models/HunyuanVideo || echo "Git clone failed, continuing..."

# Install additional dependencies
RUN pip install accelerate diffusers transformers safetensors einops decord timm pillow \\
    ffmpeg-python opencv-python imageio imageio-ffmpeg \\
    omegaconf peft bitsandbytes fairscale \\
    flask flask-cors requests tqdm huggingface_hub

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

# Create deployment script within docker
echo "Creating entrypoint script..."
cat > hunyuan-docker/entrypoint.sh << EOL
#!/bin/bash
set -e

# Configure colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\${GREEN}=== Hunyuan Video API Server ===${NC}"

# Check NVIDIA GPU
echo -e "\${BLUE}Checking NVIDIA GPU...${NC}"
nvidia-smi

# Download weights if not already present
CHECKPOINTS_DIR="/root/output/hunyuan-models"
echo -e "\${BLUE}Checking for model weights in \$CHECKPOINTS_DIR...${NC}"

# Create the directory if it doesn't exist
mkdir -p \$CHECKPOINTS_DIR

# Check if we need to download weights
if [ -z "\$(ls -A \$CHECKPOINTS_DIR 2>/dev/null)" ]; then
    echo -e "\${YELLOW}Model weights not found. Downloading...${NC}"
    
    # Check if HF_TOKEN is provided for private model repos
    if [ -n "\$HF_TOKEN" ]; then
        echo -e "\${BLUE}Using provided Hugging Face token for authentication.${NC}"
        python /root/hunyuan-models/download_weights.py --token "\$HF_TOKEN"
    else
        echo -e "\${BLUE}No HF_TOKEN provided. Attempting to download without authentication.${NC}"
        python /root/hunyuan-models/download_weights.py
    fi
else
    echo -e "\${GREEN}Model weights found. Skipping download.${NC}"
    ls -lah \$CHECKPOINTS_DIR
fi

# Get the number of model files
NUM_FILES=\$(find "\$CHECKPOINTS_DIR" -type f -name "*.bin" -o -name "*.safetensors" | wc -l)
echo -e "\${BLUE}Found \$NUM_FILES model files.${NC}"

# Parse environment variables for API server
API_ARGS=""
if [ "\$USE_CPU_OFFLOAD" = "true" ]; then
    API_ARGS="\$API_ARGS --use-cpu-offload"
fi

if [ "\$FLOW_REVERSE" = "true" ]; then
    API_ARGS="\$API_ARGS --flow-reverse"
fi

# Start the API server
echo -e "\${GREEN}Starting Hunyuan Video API Server...${NC}"
echo -e "\${BLUE}API Args: \$API_ARGS${NC}"
exec python /root/hunyuan-models/hunyuan_api.py \$API_ARGS
EOL

# Create download_weights.py
echo "Creating download_weights.py..."
cat > hunyuan-docker/download_weights.py << EOL
#!/usr/bin/env python3
"""
Script to download Hunyuan Video model weights from HuggingFace.
"""
import os
import sys
import time
import argparse
import logging
from pathlib import Path
from huggingface_hub import snapshot_download, HfApi

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
MODEL_ID = "tencent/HunyuanVideo"
CHECKPOINTS_DIR = "/root/output/hunyuan-models"

def setup_hf_auth(token):
    """Set up HuggingFace authentication"""
    if token:
        logger.info("Setting up HuggingFace authentication")
        os.environ["HUGGING_FACE_HUB_TOKEN"] = token
        api = HfApi(token=token)
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
    
    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
    
    if token and not setup_hf_auth(token):
        logger.error("Failed to authenticate with HuggingFace. Aborting download.")
        return False
    
    try:
        # Download the model weights
        logger.info(f"Downloading {MODEL_ID} to {CHECKPOINTS_DIR}...")
        start_time = time.time()
        
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
        
        # Verify download
        model_files = list(Path(CHECKPOINTS_DIR).glob("**/*.safetensors"))
        bin_files = list(Path(CHECKPOINTS_DIR).glob("**/*.bin"))
        
        logger.info(f"Found {len(model_files)} .safetensors files and {len(bin_files)} .bin files")
        
        total_size = sum(f.stat().st_size for f in model_files + bin_files) / (1024**3)
        logger.info(f"Total model size: {total_size:.2f} GB")
        
        return len(model_files) > 0 or len(bin_files) > 0
        
    except Exception as e:
        logger.error(f"Error downloading weights: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download Hunyuan Video model weights")
    parser.add_argument("--token", type=str, help="HuggingFace token for authentication")
    parser.add_argument("--model-id", type=str, default=MODEL_ID, help="HuggingFace model ID")
    parser.add_argument("--output-dir", type=str, default=CHECKPOINTS_DIR, help="Directory to save model weights")
    args = parser.parse_args()
    
    global MODEL_ID, CHECKPOINTS_DIR
    MODEL_ID = args.model_id
    CHECKPOINTS_DIR = args.output_dir
    
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

# Create placeholder hunyuan_api.py
echo "Creating placeholder hunyuan_api.py..."
cat > hunyuan-docker/hunyuan_api.py << EOL
#!/usr/bin/env python3
"""
HunyuanVideo API Server
"""
import os
import argparse
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

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
        
        # Process additional parameters
        width = data.get('width', 1280)
        height = data.get('height', 720)
        frames = data.get('frames', 129)
        steps = data.get('steps', 50)
        
        return jsonify({
            "status": "success",
            "message": "This is a placeholder API, would generate video based on prompt: " + prompt,
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
    
    app.run(host=args.host, port=args.port)
EOL

# Make scripts executable
chmod +x hunyuan-docker/entrypoint.sh

echo "Setup complete! To build and run the container, use:"
echo "docker-compose -f docker-hunyuan.yml build"
echo "docker-compose -f docker-hunyuan.yml up -d"
echo ""
echo "To check logs:"
echo "docker-compose -f docker-hunyuan.yml logs -f" 
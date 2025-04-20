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
MODEL_DIR="/root/hunyuan-models"
VENV_DIR="/root/hunyuan-venv"
HF_TOKEN="" # Add your Hugging Face token if the model is gated

echo -e "${GREEN}=== Setting up Tencent Hunyuan Model on H100 GPU ===${NC}"

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
pip install flask flask-cors transformers diffusers accelerate xformers safetensors huggingface_hub

# Set up HF token if provided
if [ ! -z "$HF_TOKEN" ]; then
    echo -e "${BLUE}Setting up Hugging Face token...${NC}"
    huggingface-cli login --token $HF_TOKEN
fi

# Clone run_hunyuan_api.py file from the backend
echo -e "${BLUE}Copying Hunyuan API code...${NC}"
if [ -f "/root/video-generation/backend/run_hunyuan_api.py" ]; then
    cp /root/video-generation/backend/run_hunyuan_api.py $MODEL_DIR/
else
    echo -e "${YELLOW}run_hunyuan_api.py not found. Will create a new one.${NC}"
    
    # Create a basic Hunyuan API script
    cat > $MODEL_DIR/run_hunyuan_api.py << 'EOF'
#!/usr/bin/env python3
"""
Flask API server for Tencent Hunyuan model running on H100 GPU
"""
import os
import time
import torch
import base64
import logging
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
from diffusers import AutoPipelineForText2Video

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Model configuration
MODEL_ID = "Tencent/hunyuan-2-video"  # Replace with actual model ID if different
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_MEMORY = {0: "70GiB"}  # For H100 80GB, allocate 70GB

# Initialize models and pipelines
logger.info(f"Loading model {MODEL_ID} on {DEVICE}")
text2video_pipe = None

def initialize_model():
    global text2video_pipe
    text2video_pipe = AutoPipelineForText2Video.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        device_map="auto",
        max_memory=MAX_MEMORY,
    )
    logger.info("Model loaded successfully")

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
        "model_loaded": text2video_pipe is not None,
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
        
        logger.info(f"Generating video for prompt: {prompt}")
        
        # Generate the video
        start_time = time.time()
        video_frames = text2video_pipe(prompt, num_inference_steps=50, height=320, width=576).frames
        
        # Save as gif for easy transmission (can be changed to mp4 if needed)
        video_path = f"/tmp/generated_video_{int(time.time())}.gif"
        
        # PIL requires a list of PIL Images
        pil_frames = [Image.fromarray(frame) for frame in video_frames]
        
        # Save as GIF
        pil_frames[0].save(
            video_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=100,  # milliseconds per frame
            loop=0,
        )
        
        # Optionally encode as base64 for direct transmission
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
        })
    
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Initialize the model
    initialize_model()
    
    # Start the Flask server
    logger.info("Starting Flask server")
    app.run(host='0.0.0.0', port=8000, debug=False)
EOF
fi

# Create a systemd service file for the API
echo -e "${BLUE}Creating systemd service for Hunyuan API...${NC}"
cat > /etc/systemd/system/hunyuan-api.service << EOF
[Unit]
Description=Hunyuan API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$MODEL_DIR
ExecStart=$VENV_DIR/bin/python $MODEL_DIR/run_hunyuan_api.py
Restart=on-failure
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=hunyuan-api
Environment="PYTHONPATH=$MODEL_DIR"

[Install]
WantedBy=multi-user.target
EOF

# Create a startup script
echo -e "${BLUE}Creating startup script...${NC}"
cat > $MODEL_DIR/start-hunyuan-api.sh << EOF
#!/bin/bash
source $VENV_DIR/bin/activate
cd $MODEL_DIR
python run_hunyuan_api.py
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

echo -e "${GREEN}=== Hunyuan Model Setup Complete! ===${NC}"
echo -e "${YELLOW}The Hunyuan API is running at: http://localhost:8000${NC}"
echo -e "${YELLOW}Test endpoints:${NC}"
echo -e "  - Health check: curl http://localhost:8000/health"
echo -e "  - Generate video: curl -X POST -H 'Content-Type: application/json' -d '{\"prompt\":\"A cat playing piano\"}' http://localhost:8000/generate-video"
echo -e "\n${YELLOW}To restart the service:${NC} systemctl restart hunyuan-api.service"
echo -e "${YELLOW}To view logs:${NC} journalctl -u hunyuan-api.service -f" 
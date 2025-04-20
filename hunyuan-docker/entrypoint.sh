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
CHECKPOINTS_DIR="/root/output/hunyuan-models"
echo -e "${BLUE}Checking for model weights in $CHECKPOINTS_DIR...${NC}"

# Create the directory if it doesn't exist
mkdir -p $CHECKPOINTS_DIR

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
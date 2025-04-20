#!/bin/bash
set -e

echo "Preparing H100 deployment for Hunyuan on Digital Ocean..."

# Create output directory for model storage
mkdir -p output/hunyuan-models
echo "Created output directory for model storage"

# Check if HF_TOKEN is set
if [ -z "${HF_TOKEN}" ]; then
  echo "ERROR: HF_TOKEN environment variable is not set!"
  echo "You need a Hugging Face token with access to tencent/HunyuanVideo"
  echo "Create one at https://huggingface.co/settings/tokens"
  echo "Then set it with: export HF_TOKEN=your_token_here"
  exit 1
fi

# Create .env file for docker-compose
echo "Creating .env file with your HF_TOKEN..."
echo "HF_TOKEN=${HF_TOKEN}" > .env

# Verify NVIDIA drivers are working
echo "Checking NVIDIA drivers..."
if ! nvidia-smi > /dev/null 2>&1; then
  echo "ERROR: nvidia-smi failed. Please ensure NVIDIA drivers are properly installed."
  echo "For Digital Ocean, you should select a Droplet with GPU enabled."
  exit 1
fi

echo "NVIDIA drivers detected:"
nvidia-smi

# Verify Docker can access the GPU
echo "Checking Docker NVIDIA runtime..."
if ! docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
  echo "ERROR: Docker cannot access the GPU."
  echo "Make sure nvidia-container-toolkit is installed properly."
  echo "For Digital Ocean, this should be preconfigured on GPU-enabled Droplets."
  exit 1
fi

echo "Docker NVIDIA runtime is working correctly."

# Build and run with H100 configuration
echo "Building and starting Hunyuan container optimized for H100..."
docker-compose -f docker-hunyuan-h100.yml build
docker-compose -f docker-hunyuan-h100.yml up -d

echo "Checking logs..."
docker-compose -f docker-hunyuan-h100.yml logs

echo "Deployment complete! The API will be available at http://localhost:8000 once initialization is finished."
echo "You can check the progress with: docker-compose -f docker-hunyuan-h100.yml logs -f" 
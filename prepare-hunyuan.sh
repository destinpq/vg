#!/bin/bash
set -e

echo "Preparing environment for HunyuanVideo Docker setup..."

# Create output directory for model storage
mkdir -p output/hunyuan-models
echo "Created output directory for model storage"

# Check if HF_TOKEN is set
if [ -z "${HF_TOKEN}" ]; then
  echo "Warning: HF_TOKEN environment variable is not set!"
  echo "You need a Hugging Face token with access to tencent/HunyuanVideo"
  echo "Create one at https://huggingface.co/settings/tokens"
  echo "Then set it with: export HF_TOKEN=your_token_here"
  echo ""
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env file for Docker Compose..."
  echo "HF_TOKEN=${HF_TOKEN:-default_token_for_testing}" > .env
  echo ".env file created"
fi

echo "Environment is prepared!"
echo "You can now run:"
echo "  docker-compose -f docker-hunyuan-gpu.yml build"
echo "  docker-compose -f docker-hunyuan-gpu.yml up -d"
echo ""
echo "Models will be downloaded to: ./output/hunyuan-models" 
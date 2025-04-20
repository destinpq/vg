#!/bin/bash
set -e

echo "Deploying Hunyuan Video Generation in CPU fallback mode..."

# Create output directory for model storage
mkdir -p output/hunyuan-models
echo "Created output directory for model storage"

# Check if HF_TOKEN is set
if [ -z "${HF_TOKEN}" ]; then
  echo "WARNING: HF_TOKEN environment variable is not set!"
  echo "You need a Hugging Face token with access to tencent/HunyuanVideo"
  echo "Create one at https://huggingface.co/settings/tokens"
  echo "Then set it with: export HF_TOKEN=your_token_here"
  read -p "Would you like to continue without a token? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Create .env file for docker-compose
echo "Creating .env file with your HF_TOKEN..."
echo "HF_TOKEN=${HF_TOKEN:-default_token_for_testing}" > .env

# Update docker-compose file for CPU-only mode
echo "Updating docker-compose configuration for CPU-only mode..."
cat > docker-hunyuan-cpu.yml << EOL
services:
  hunyuan-api:
    build:
      context: ./hunyuan-docker
      dockerfile: Dockerfile.minimal
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - ./output:/root/output
    environment:
      - HF_TOKEN=\${HF_TOKEN:-default_token_for_testing}
      - USE_CPU_OFFLOAD=true
      - FLOW_REVERSE=true
      - MODEL_DIR=/root/output/hunyuan-models
      - NVIDIA_VISIBLE_DEVICES=""
      - CUDA_VISIBLE_DEVICES=-1
    healthcheck:
      test: ["CMD-SHELL", "curl -s -f http://localhost:8000/health > /dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
EOL

# Switch to minimal setup
echo "Setting up minimal configuration..."
if [ -f "use-minimal-setup.sh" ]; then
  ./use-minimal-setup.sh
else
  echo "WARNING: use-minimal-setup.sh not found, assuming minimal setup is already in place."
fi

# Build and start the container
echo "Building and starting Hunyuan container in CPU-only mode..."
docker-compose -f docker-hunyuan-cpu.yml build
docker-compose -f docker-hunyuan-cpu.yml up -d

# Show logs to track progress
echo "Showing container logs (press Ctrl+C to exit logs, container will keep running)..."
docker-compose -f docker-hunyuan-cpu.yml logs -f

echo "Hunyuan API will be available at http://localhost:8000 once initialization is complete."
echo "Note: Running in CPU-only mode will be significantly slower than with GPU acceleration."
echo "To check status: docker-compose -f docker-hunyuan-cpu.yml logs -f" 
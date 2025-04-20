#!/bin/bash
set -e

# Check if HF_TOKEN is set
if [ -z "${HF_TOKEN}" ]; then
  echo "Warning: HF_TOKEN environment variable is not set!"
  echo "You need a Hugging Face token with access to tencent/HunyuanVideo"
  echo "Create one at https://huggingface.co/settings/tokens"
  echo "Then set it with: export HF_TOKEN=your_token_here"
  echo "Continuing build, but model weights download may fail later..."
  echo ""
fi

echo "Creating temporary build directory..."
rm -rf .build-hunyuan
mkdir -p .build-hunyuan

echo "Copying Dockerfile and required files..."
cp hunyuan-docker/Dockerfile .build-hunyuan/
cp hunyuan-docker/hunyuan_api.py .build-hunyuan/
cp hunyuan-docker/download_weights.py .build-hunyuan/
cp hunyuan-docker/entrypoint.sh .build-hunyuan/

echo "Creating temporary docker-compose file..."
cat > docker-hunyuan-temp.yml << EOL
services:
  hunyuan-api:
    build:
      context: ./.build-hunyuan
      dockerfile: Dockerfile
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - hunyuan-weights:/root/hunyuan-models/HunyuanVideo/ckpts
      - ./output:/root/output
    environment:
      - HF_TOKEN=\${HF_TOKEN:-default_token_for_testing}
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

echo "Building Docker image..."
docker-compose -f docker-hunyuan-temp.yml build

echo "Cleaning up..."
rm -rf .build-hunyuan docker-hunyuan-temp.yml

echo "Done! You can now run: docker-compose -f docker-hunyuan-gpu.yml up -d" 
#!/bin/bash
set -e

echo "Switching to minimal Hunyuan setup..."

# Make backup of original files
echo "Creating backups of original files..."
mkdir -p hunyuan-docker/backups
cp hunyuan-docker/Dockerfile hunyuan-docker/backups/Dockerfile.original
cp hunyuan-docker/entrypoint.sh hunyuan-docker/backups/entrypoint.sh.original
cp hunyuan-docker/download_weights.py hunyuan-docker/backups/download_weights.py.original

# Copy minimal versions to main locations
echo "Copying minimal setup files..."
cp hunyuan-docker/Dockerfile.minimal hunyuan-docker/Dockerfile
cp hunyuan-docker/entrypoint.minimal.sh hunyuan-docker/entrypoint.sh
cp hunyuan-docker/download_weights.minimal.py hunyuan-docker/download_weights.py

echo "Making entrypoint.sh executable..."
chmod +x hunyuan-docker/entrypoint.sh

echo "Successfully switched to minimal setup!"
echo "You can now run:"
echo "  ./prepare-hunyuan.sh"
echo "  docker-compose -f docker-hunyuan-minimal.yml build"
echo "  docker-compose -f docker-hunyuan-minimal.yml up -d" 
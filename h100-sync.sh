#!/bin/bash
# H100 GPU Sync Script for AI Engine
# This script synchronizes ai_engine changes directly to the H100 GPU server
# and updates the Docker containers

set -e  # Exit on any error

# Configuration
H100_SERVER="root@your-h100-server-ip"  # Replace with your H100 server IP
GPU_APP_DIR="/root/video-generation"     # App directory on H100 server
LOCAL_AI_ENGINE_DIR="$(pwd)/ai_engine"   # Local ai_engine directory

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== H100 GPU Sync Tool for AI Engine ===${NC}"

# Check if the ai_engine directory exists
if [ ! -d "$LOCAL_AI_ENGINE_DIR" ]; then
  echo -e "${RED}Error: ai_engine directory not found at $LOCAL_AI_ENGINE_DIR${NC}"
  exit 1
fi

# Check SSH connection to H100 server
echo -e "${BLUE}Checking connection to H100 server...${NC}"
if ! ssh -q -o BatchMode=yes -o ConnectTimeout=5 $H100_SERVER echo > /dev/null 2>&1; then
  echo -e "${RED}Cannot connect to H100 server at $H100_SERVER${NC}"
  echo -e "${YELLOW}Please check:${NC}"
  echo -e "  1. The server IP is correct"
  echo -e "  2. SSH keys are set up properly (use setup-ssh-key.sh)"
  echo -e "  3. The server is running and accessible"
  exit 1
fi

echo -e "${GREEN}Connection to H100 server successful!${NC}"

# Create GPU_APP_DIR if it doesn't exist
echo -e "${BLUE}Ensuring application directory exists on H100 server...${NC}"
ssh $H100_SERVER "mkdir -p $GPU_APP_DIR"

# Sync ai_engine directory to H100 server
echo -e "${YELLOW}Synchronizing ai_engine to H100 server...${NC}"
rsync -avz --delete $LOCAL_AI_ENGINE_DIR/ $H100_SERVER:$GPU_APP_DIR/ai_engine/

# Check if Docker is installed on H100 server
echo -e "${BLUE}Checking Docker installation on H100 server...${NC}"
if ! ssh $H100_SERVER "command -v docker > /dev/null && command -v docker-compose > /dev/null"; then
  echo -e "${RED}Docker or Docker Compose not found on H100 server.${NC}"
  echo -e "${YELLOW}Please run the setup-server-cicd.sh script on the H100 server first.${NC}"
  exit 1
fi

# Restart Docker containers on H100 server
echo -e "${YELLOW}Restarting Docker containers on H100 server...${NC}"
ssh $H100_SERVER "cd $GPU_APP_DIR && docker-compose down && docker-compose build && docker-compose up -d"

echo -e "${GREEN}AI Engine successfully synchronized with H100 GPU server!${NC}"
echo -e "${BLUE}Container status on H100 server:${NC}"
ssh $H100_SERVER "cd $GPU_APP_DIR && docker-compose ps"

# Optional GPU status check
echo -e "${BLUE}GPU status on H100 server:${NC}"
ssh $H100_SERVER "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader" 
#!/bin/bash
# Auto-push script for Video Generation application
# This script:
# 1. Checks for changes in backend, frontend, and ai_engine directories
# 2. Commits and pushes changes to GitHub
# 3. Ensures ai_engine and backend changes are deployed to H100 GPU

set -e  # Exit on any error

# Configuration
REPO_DIR="$(pwd)"
REMOTE="origin"
BRANCH="main"  # Change this to your default branch if different
COMMIT_MSG="Auto-update: $(date '+%Y-%m-%d %H:%M:%S')"
H100_SERVER="root@your-h100-server-ip"  # Change to your H100 server IP
GPU_APP_DIR="/root/video-generation"    # App directory on GPU server

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if directories exist
for dir in "backend" "frontend" "ai_engine"; do
  if [ ! -d "$dir" ]; then
    echo -e "${RED}Error: $dir directory not found${NC}"
    exit 1
  fi
done

# Function to check if directory has changes
has_changes() {
  local dir=$1
  git status --porcelain "$dir" | grep -q .
  return $?
}

# Function to commit and push changes for a specific directory
commit_and_push() {
  local dir=$1
  local message="${2:-$COMMIT_MSG}"
  
  echo -e "${BLUE}Processing $dir changes...${NC}"
  
  if has_changes "$dir"; then
    echo -e "${YELLOW}Changes detected in $dir. Committing...${NC}"
    git add "$dir"
    git commit -m "$message [$dir]"
    echo -e "${GREEN}Changes committed for $dir${NC}"
    
    echo -e "${YELLOW}Pushing changes to $REMOTE/$BRANCH...${NC}"
    git push $REMOTE $BRANCH
    echo -e "${GREEN}Changes pushed successfully for $dir${NC}"
    return 0  # Changes were made and pushed
  else
    echo -e "${GREEN}No changes detected in $dir. Skipping.${NC}"
    return 1  # No changes
  fi
}

# Function to deploy ai_engine and backend changes to H100 GPU
deploy_to_gpu() {
  echo -e "${BLUE}Deploying changes to H100 GPU...${NC}"
  
  # First check if we can connect to the server
  if ! ssh -q -o BatchMode=yes -o ConnectTimeout=5 $H100_SERVER echo > /dev/null 2>&1; then
    echo -e "${RED}Cannot connect to H100 server. Check SSH connection and server status.${NC}"
    return 1
  fi
  
  # Check if we should sync ai_engine
  if [ "$1" == "ai_engine" ] || [ "$1" == "both" ]; then
    # Copy the ai_engine directory to the H100 server
    echo -e "${YELLOW}Copying ai_engine files to H100 server...${NC}"
    rsync -avz --delete ./ai_engine/ $H100_SERVER:$GPU_APP_DIR/ai_engine/
  fi
  
  # Check if we should sync backend
  if [ "$1" == "backend" ] || [ "$1" == "both" ]; then
    # Copy the backend directory to the H100 server
    echo -e "${YELLOW}Copying backend files to H100 server...${NC}"
    rsync -avz --delete ./backend/ $H100_SERVER:$GPU_APP_DIR/backend/
  fi
  
  # Restart the container on the H100 server
  echo -e "${YELLOW}Rebuilding and restarting Docker containers on H100 server...${NC}"
  ssh $H100_SERVER "cd $GPU_APP_DIR && docker-compose down && docker-compose build backend && docker-compose up -d"
  
  echo -e "${GREEN}Changes deployed to H100 GPU successfully!${NC}"
  
  # Check container logs for Python errors
  echo -e "${YELLOW}Checking for Python errors in container logs...${NC}"
  ssh $H100_SERVER "cd $GPU_APP_DIR && docker-compose logs --tail=20 backend | grep -i error || echo 'No errors found in logs'"
}

# Main execution
echo -e "${GREEN}=== Auto-Push for Video Generation App ===${NC}"
echo -e "${YELLOW}Checking for changes in backend, frontend, and ai_engine...${NC}"

# Make sure we're in the repo directory
cd "$REPO_DIR"

# Get latest changes from remote
echo -e "${BLUE}Fetching latest changes from remote...${NC}"
git fetch $REMOTE $BRANCH

# Process backend changes
commit_and_push "backend" "Backend update: $(date '+%Y-%m-%d %H:%M:%S')"
backend_pushed=$?

# Process frontend changes
commit_and_push "frontend" "Frontend update: $(date '+%Y-%m-%d %H:%M:%S')"
frontend_pushed=$?

# Process ai_engine changes and deploy to GPU if changes were made
commit_and_push "ai_engine" "AI Engine update: $(date '+%Y-%m-%d %H:%M:%S')"
ai_engine_pushed=$?

# Deploy changes to GPU if needed
if [ $ai_engine_pushed -eq 0 ] && [ $backend_pushed -eq 0 ]; then
  # Both ai_engine and backend changed
  deploy_to_gpu "both"
elif [ $ai_engine_pushed -eq 0 ]; then
  # Only ai_engine changed
  deploy_to_gpu "ai_engine"
elif [ $backend_pushed -eq 0 ]; then
  # Only backend changed
  deploy_to_gpu "backend"
else
  echo -e "${BLUE}No backend or ai_engine changes to deploy to H100 GPU.${NC}"
fi

# Summary
echo -e "\n${GREEN}=== Summary ===${NC}"
if [ $backend_pushed -eq 0 ] || [ $frontend_pushed -eq 0 ] || [ $ai_engine_pushed -eq 0 ]; then
  echo -e "${GREEN}Changes successfully pushed to GitHub.${NC}"
  if [ $ai_engine_pushed -eq 0 ] || [ $backend_pushed -eq 0 ]; then
    echo -e "${GREEN}Changes deployed to H100 GPU.${NC}"
  fi
else
  echo -e "${YELLOW}No changes detected in any directories.${NC}"
fi

echo -e "${GREEN}Done!${NC}" 
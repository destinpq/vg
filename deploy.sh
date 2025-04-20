#!/bin/bash
# Automatic deployment script for Video Generation app
# This script watches for changes, pulls from git, and redeploys the Docker containers

set -e  # Exit on any error

# Configuration
APP_DIR="/root/video-generation"  # Change to your application directory
BRANCH="main"                    # Change to your main branch
REMOTE="origin"                  # Git remote name

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Video Generation App Deployment Service ===${NC}"
echo -e "${YELLOW}This script will continuously check for updates and deploy them.${NC}"

# Create a deployment log
mkdir -p "${APP_DIR}/logs"
LOGFILE="${APP_DIR}/logs/deployment.log"
touch $LOGFILE

# Function to log messages
log() {
  local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo -e "$message"
  echo "$message" >> $LOGFILE
}

# Function to check and handle changes
deploy_changes() {
  log "${GREEN}Checking for code changes...${NC}"
  
  # Navigate to app directory
  cd "$APP_DIR"
  
  # Fetch latest code
  git fetch $REMOTE $BRANCH
  
  # Check if we need to pull changes
  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git rev-parse $REMOTE/$BRANCH)
  
  if [ "$LOCAL" != "$REMOTE" ]; then
    log "${YELLOW}Changes detected! Deploying...${NC}"
    
    # Pull the latest changes
    git pull $REMOTE $BRANCH
    
    # Build and restart the containers
    log "${GREEN}Rebuilding and restarting Docker containers...${NC}"
    docker-compose down
    docker-compose build
    docker-compose up -d
    
    log "${GREEN}Deployment completed successfully!${NC}"
  else
    log "No changes detected."
  fi
}

# Main execution
cd "$APP_DIR" || {
  log "${RED}Error: Application directory $APP_DIR not found${NC}"
  exit 1
}

# Initial deployment
deploy_changes

# Setup continuous deployment
log "${GREEN}Setting up continuous deployment watcher...${NC}"
log "Press Ctrl+C to stop the deployment service"

while true; do
  deploy_changes
  log "Waiting for changes... (checking every 5 minutes)"
  sleep 300  # Check every 5 minutes
done 
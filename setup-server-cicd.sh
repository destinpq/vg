#!/bin/bash
# Setup CI/CD on Digital Ocean server
# Run this script on your Digital Ocean server

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Setting up CI/CD on Digital Ocean Server ===${NC}"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
  echo -e "${RED}This script must be run as root${NC}"
  exit 1
fi

# Required packages
echo -e "${YELLOW}Installing required packages...${NC}"
apt-get update
apt-get install -y git tmux

# Create app directory
APP_DIR="/root/video-generation"
mkdir -p "$APP_DIR"

# Clone the repository if not already cloned
if [ ! -d "$APP_DIR/.git" ]; then
  echo -e "${YELLOW}Cloning repository...${NC}"
  read -p "Enter your Git repository URL: " REPO_URL
  git clone "$REPO_URL" "$APP_DIR"
else
  echo -e "${YELLOW}Repository already exists, skipping clone${NC}"
fi

# Navigate to app directory
cd "$APP_DIR"

# Copy deployment script to the app directory
cp /path/to/deploy.sh "$APP_DIR/deploy.sh"
chmod +x "$APP_DIR/deploy.sh"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
  echo -e "${YELLOW}Docker not found. Installing Docker...${NC}"
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  usermod -aG docker $USER
  
  # Install Docker Compose
  echo -e "${YELLOW}Installing Docker Compose...${NC}"
  curl -L "https://github.com/docker/compose/releases/download/v2.17.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
else
  echo -e "${GREEN}Docker already installed${NC}"
fi

# Create systemd service for continuous deployment
echo -e "${YELLOW}Setting up deployment service...${NC}"

cat > /etc/systemd/system/video-generation-deploy.service << EOF
[Unit]
Description=Video Generation Deployment Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/deploy.sh
Restart=on-failure
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=video-generation-deploy

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable video-generation-deploy.service
systemctl start video-generation-deploy.service

echo -e "${GREEN}CI/CD setup completed!${NC}"
echo -e "${YELLOW}Deployment service is now running and will automatically deploy changes.${NC}"
echo -e "${YELLOW}You can monitor the service with: systemctl status video-generation-deploy${NC}"
echo -e "${YELLOW}Check logs with: journalctl -u video-generation-deploy${NC}"

# Provide instructions for webhook setup (optional, for future use)
echo -e "\n${GREEN}=== OPTIONAL: Setting up a webhook (for future use) ===${NC}"
echo -e "${YELLOW}You could also set up a webhook for GitHub/GitLab integration:${NC}"
echo -e "1. Install a webhook server: apt-get install webhook"
echo -e "2. Create a webhook configuration for your repository"
echo -e "3. Connect it to your repository's webhook settings"
echo -e "${YELLOW}This would allow automatic deployments on push to your repository.${NC}" 
#!/bin/bash
# Setup a systemd service for the auto-push script to run every hour

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Setting up Auto-Push Service ===${NC}"

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
  echo -e "${RED}This script must be run as root${NC}"
  exit 1
fi

# Get the absolute path to the auto-push script
SCRIPT_PATH="$(pwd)/auto-push.sh"

if [ ! -f "$SCRIPT_PATH" ]; then
  echo -e "${RED}Error: auto-push.sh not found in current directory${NC}"
  exit 1
fi

# Make the script executable
chmod +x "$SCRIPT_PATH"

# Create a systemd service file
echo -e "${YELLOW}Creating systemd service and timer...${NC}"

# Service file
cat > /etc/systemd/system/video-generation-auto-push.service << EOF
[Unit]
Description=Video Generation Auto-Push Service
After=network.target

[Service]
Type=oneshot
ExecStart=$SCRIPT_PATH
WorkingDirectory=$(pwd)
User=$(whoami)
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Timer file (to run the service on a schedule)
cat > /etc/systemd/system/video-generation-auto-push.timer << EOF
[Unit]
Description=Run Video Generation Auto-Push hourly

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h
AccuracySec=1min

[Install]
WantedBy=timers.target
EOF

# Reload systemd, enable and start the timer
systemctl daemon-reload
systemctl enable video-generation-auto-push.timer
systemctl start video-generation-auto-push.timer

echo -e "${GREEN}Auto-Push service installed successfully!${NC}"
echo -e "${YELLOW}The auto-push script will run:${NC}"
echo -e "  - 5 minutes after system boot"
echo -e "  - Every hour after that"
echo -e "${YELLOW}You can check status with:${NC}"
echo -e "  systemctl status video-generation-auto-push.timer"
echo -e "  systemctl list-timers"
echo -e "${YELLOW}You can run it manually with:${NC}"
echo -e "  systemctl start video-generation-auto-push.service"
echo -e "${YELLOW}You can view logs with:${NC}"
echo -e "  journalctl -u video-generation-auto-push" 
#!/bin/bash
# Setup Git hooks for automatic deployment

set -e  # Exit on any error

# Configuration
REPO_DIR="$(pwd)"  # Current directory, change if needed
HOOKS_DIR="$REPO_DIR/.git/hooks"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Setting up Git hooks for automatic deployment ===${NC}"

# Ensure hooks directory exists
mkdir -p "$HOOKS_DIR"

# Create post-commit hook to push changes automatically
cat > "$HOOKS_DIR/post-commit" << 'EOF'
#!/bin/bash
# Git post-commit hook to automatically push changes

BRANCH=$(git rev-parse --abbrev-ref HEAD)
REMOTE="origin"

echo -e "\033[0;33mAuto-pushing commit to $REMOTE/$BRANCH...\033[0m"
git push $REMOTE $BRANCH

if [ $? -eq 0 ]; then
  echo -e "\033[0;32mChanges pushed successfully! Deployment should start automatically.\033[0m"
else
  echo -e "\033[0;31mError pushing changes. You may need to push manually with 'git push'.\033[0m"
fi
EOF

# Make the hook executable
chmod +x "$HOOKS_DIR/post-commit"

# Create a simple pre-commit hook to verify changes
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# Git pre-commit hook to verify changes

echo -e "\033[0;33mVerifying changes before commit...\033[0m"

# Add any validation you want here
# For example, check if Docker and docker-compose are available
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
  echo -e "\033[0;31mDocker or docker-compose not found. Please install them first.\033[0m"
  exit 1
fi

echo -e "\033[0;32mAll checks passed. Proceeding with commit.\033[0m"
exit 0
EOF

# Make the hook executable
chmod +x "$HOOKS_DIR/pre-commit"

echo -e "${GREEN}Git hooks installed successfully!${NC}"
echo -e "${YELLOW}Now when you commit changes, they will be automatically pushed to remote.${NC}"
echo -e "${YELLOW}The server-side deploy.sh script will handle the deployment.${NC}" 
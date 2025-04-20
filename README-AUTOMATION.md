# Automated Deployment Scripts for Video Generation

This README explains how to use the automation scripts to push code changes to GitHub and deploy Python backend and AI Engine changes to your H100 GPU server.

## Scripts Overview

1. **auto-push.sh**: Automatically commits and pushes changes in backend, frontend, and ai_engine directories to GitHub. Also deploys backend and ai_engine changes to H100 GPU.

2. **h100-sync.sh**: Specifically designed to synchronize backend and ai_engine changes to your H100 GPU server. Useful for manual GPU deployments.

3. **auto-deploy-service.sh**: Sets up a systemd service that runs the auto-push script automatically on a schedule.

## Setup Instructions

### 1. Edit Configuration in Scripts

Before using these scripts, you need to update the configuration variables:

In **auto-push.sh** and **h100-sync.sh**:
```bash
# Change these variables
H100_SERVER="root@your-h100-server-ip"  # Replace with your H100 server IP
GPU_APP_DIR="/root/video-generation"    # App directory on H100 server
BRANCH="main"                           # Your default Git branch
```

### 2. Make Scripts Executable

```bash
chmod +x auto-push.sh h100-sync.sh auto-deploy-service.sh
```

### 3. Setup SSH Access to H100 Server

If you haven't already configured SSH access to your H100 server:

```bash
# On your H100 server, run the SSH setup script
./setup-ssh-key.sh

# Test connection from your local machine
ssh root@your-h100-server-ip
```

## Python Backend Information

The Docker configuration has been optimized for a Python backend:

- Uses a Python virtual environment for clean dependency management
- Includes specific PyTorch installation with CUDA support for the H100 GPU
- Sets proper Python paths and environment variables
- Includes health checks to ensure services are running properly
- Mounts the ai_engine directory as a volume for faster development
- Includes automatic error log checking after deployments

## Usage

### Manual Pushing

To manually push changes and deploy:

```bash
# Run the auto-push script
./auto-push.sh
```

This will:
1. Check for changes in backend, frontend, and ai_engine
2. Commit and push changes to GitHub
3. Deploy backend and ai_engine changes to your H100 GPU if any were detected

### Manual Backend and AI Engine Sync

To specifically sync backend and ai_engine changes to your H100 GPU:

```bash
# Run the H100 sync script
./h100-sync.sh
```

### Automated Deployment

To set up automated deployment (needs root/sudo):

```bash
# Setup the auto-deployment service
sudo ./auto-deploy-service.sh
```

This creates a systemd service that:
1. Runs 5 minutes after system boot
2. Runs every hour afterwards
3. Automatically pushes changes and deploys to H100 GPU

### Checking Service Status

After setting up the automated service:

```bash
# Check if the service is running
systemctl status video-generation-auto-push.timer

# List all active timers
systemctl list-timers

# View the logs
journalctl -u video-generation-auto-push
```

## Integration with Cursor AI

When working with Cursor AI:

1. Connect to your project on your local machine or directly on the server
2. Make changes to backend, frontend, or ai_engine
3. The auto-push system will detect these changes and:
   - Push them to GitHub
   - Deploy backend and ai_engine changes to your H100 GPU

You can commit manually or let the automated service handle it hourly.

## Troubleshooting

### Python-specific Issues

If you encounter Python errors:

1. Check container logs: `docker-compose logs backend`
2. Verify Python dependencies are installed:
   ```bash
   docker-compose exec backend pip list
   ```
3. Check Python version: 
   ```bash
   docker-compose exec backend python --version
   ```
4. Check for import errors in logs:
   ```bash
   docker-compose logs backend | grep "ImportError"
   ```

### Connection Issues to H100 Server

If you're having issues connecting to the H100 server:

1. Verify the server IP is correct
2. Check that SSH keys are properly set up
3. Ensure the server is running and accessible
4. Verify network connectivity: `ping your-h100-server-ip`

### Git Push Failures

If Git push fails:

1. Check that you have the proper permissions on the repository
2. Verify your Git remote is set up correctly: `git remote -v`
3. Ensure there are no merge conflicts

### Docker Issues on H100 Server

If container deployment fails:

1. SSH into the H100 server
2. Check Docker status: `systemctl status docker`
3. Verify docker-compose is installed: `docker-compose --version`
4. Check container logs: `docker-compose logs`

## Advanced Configuration

For more advanced setups, you can modify:

- **Sync frequency**: Edit the timer in `auto-deploy-service.sh`
- **Git commit messages**: Customize in `auto-push.sh`
- **Deployment options**: Add additional Docker commands in `h100-sync.sh`
- **Python packages**: Edit the Docker files to include additional Python packages 
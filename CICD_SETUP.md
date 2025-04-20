# CI/CD Setup for Video Generation Application

This guide explains how to set up a continuous integration and continuous deployment (CI/CD) pipeline for the Video Generation application, allowing you to work in Cursor and have your changes automatically deployed to your Digital Ocean server.

## Overview

The CI/CD pipeline consists of:

1. **Local development** using Cursor AI connected to your Digital Ocean server
2. **Git hooks** that automatically push your changes when you commit
3. **Server-side deployment service** that detects changes and rebuilds Docker containers

## Setup Instructions

### 1. Local Development Setup

First, ensure you can connect to your Digital Ocean server using SSH:

```bash
# Make the SSH key setup script executable
chmod +x setup-ssh-key.sh

# Run the script on your Digital Ocean server
# (You'll need to transfer it to your server first)
./setup-ssh-key.sh
```

Then, connect to your server using Cursor AI:

1. Install the "Remote - SSH" extension in Cursor AI
2. Configure SSH connection to your Digital Ocean server
3. Connect and open your project folder

### 2. Server-Side CI/CD Setup

Run the following script on your Digital Ocean server to set up the deployment service:

```bash
# Make the script executable
chmod +x setup-server-cicd.sh

# Run the script (must be run as root)
sudo ./setup-server-cicd.sh
```

This script will:
- Install Git and other required packages
- Set up a systemd service that watches for Git changes
- Configure Docker and Docker Compose

### 3. Git Hooks Setup (on your local machine or Cursor AI)

Run the following script in your local repository to set up Git hooks:

```bash
# Make the script executable
chmod +x setup-git-hooks.sh

# Run the script
./setup-git-hooks.sh
```

This sets up Git hooks that:
- Verify your changes before committing
- Automatically push changes after committing

## How It Works

Once set up, the workflow is:

1. **Develop in Cursor AI** connected to your Digital Ocean server
2. **Commit your changes** using Git (Cursor AI has Git integration)
3. Git hooks **automatically push** your changes to the repository
4. The server-side deployment service **detects the changes**
5. Docker containers are **rebuilt and restarted** automatically

## Troubleshooting

### Deployment Not Working

Check the deployment service status:

```bash
sudo systemctl status video-generation-deploy
```

View deployment logs:

```bash
sudo journalctl -u video-generation-deploy
```

### Git Hook Issues

If the automatic push isn't working:

1. Check if the Git hooks are executable:
   ```bash
   ls -la .git/hooks/
   ```

2. Try pushing manually:
   ```bash
   git push origin main
   ```

### Docker Issues

Check Docker and Docker Compose installation:

```bash
docker --version
docker-compose --version
```

Make sure the Docker daemon is running:

```bash
sudo systemctl status docker
```

## Advanced Configuration

For more advanced setups, consider:

1. **GitHub/GitLab Webhooks**: For triggering deployments directly from GitHub/GitLab
2. **Environment-specific deployments**: Different configurations for staging/production
3. **Automated testing**: Add tests before deployment

Refer to the comments in the deployment scripts for more information on these options. 
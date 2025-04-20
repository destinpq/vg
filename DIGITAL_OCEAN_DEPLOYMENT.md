# Deploying to Digital Ocean with H100 GPU

This guide provides instructions for deploying the AI Video Generation application on Digital Ocean with a H100x1-80GB GPU.

## Prerequisites

- A Digital Ocean account with billing set up
- Docker and Docker Compose installed on your local machine
- Git installed on your local machine

## 1. Create a Digital Ocean Droplet with GPU

1. Log in to your Digital Ocean account
2. Go to the "Create" dropdown and select "Droplets"
3. In the "Choose an image" section, select "Marketplace" and search for "Docker"
4. Select the "Docker" image
5. In the "Choose a plan" section, select "GPU Optimized" 
6. Choose the "GPU Standard - H100 80GB" plan with 1 H100 GPU
7. Select any additional options as needed (e.g., monitoring, backups)
8. Add your SSH key if you haven't already
9. Click "Create Droplet"

## 2. Connect to Your Droplet

Once your droplet is created, you can connect to it using SSH:

```bash
ssh root@your-droplet-ip
```

## 3. Set Up the Server

Update your server and install required dependencies:

```bash
# Update the system
apt-get update && apt-get upgrade -y

# Install NVIDIA drivers and CUDA
# Digital Ocean GPU droplets should have the drivers pre-installed
# Check if the drivers are installed
nvidia-smi

# If not installed, follow NVIDIA's instructions to install CUDA drivers
# https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html
```

## 4. Clone the Repository

```bash
git clone https://your-repository-url.git
cd video-generation
```

## 5. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
EOF
```

## 6. Deploy with Docker Compose

```bash
# Build and start the containers
docker-compose up -d

# Check that both services are running
docker-compose ps
```

## 7. Test the Deployment

Test that the backend is running:

```bash
curl http://localhost:5001
```

You should see a JSON response with information about the API.

Test that the frontend is running:

```bash
curl http://localhost:3000
```

You should see the HTML content of the frontend application.

## 8. Setting Up a Domain Name (Optional)

To use a custom domain name for your application:

1. Add an A record in your domain's DNS settings pointing to your Digital Ocean droplet's IP address
2. Install Nginx as a reverse proxy:

```bash
apt-get install -y nginx
```

3. Create an Nginx configuration file:

```bash
cat > /etc/nginx/sites-available/videogen << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:5001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable the site
ln -s /etc/nginx/sites-available/videogen /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

4. Set up HTTPS with Certbot:

```bash
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

## 9. Monitoring and Scaling

Monitor GPU usage:

```bash
nvidia-smi -l 1  # Updates every 1 second
```

For persistent monitoring, consider setting up:

- Prometheus for metrics collection
- Grafana for visualization

## 10. Development with Cursor AI

To develop directly on your Digital Ocean droplet using Cursor AI:

1. Install the Cursor AI Remote Extension:
   - Open Cursor AI on your local machine
   - Go to Extensions
   - Search for "Remote - SSH" and install it

2. Configure SSH in Cursor AI:
   - Click on the Remote Explorer tab in the sidebar
   - Click on "+" to add a new SSH host
   - Enter: `ssh root@your-droplet-ip`
   - Select the SSH configuration file to update
   - Connect to the host

3. Open your project folder:
   - Once connected to the remote host, click "Open Folder"
   - Navigate to your project directory and click "OK"

4. You can now edit files directly on the Digital Ocean droplet using Cursor AI

## Debugging

If you encounter issues:

1. Check the container logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

2. Check GPU utilization:
```bash
nvidia-smi
```

3. Check that the containers can communicate with each other:
```bash
docker network inspect video-generation_default
```

## Backups

Regular backups are recommended:

```bash
# Create a snapshot of your Droplet
doctl compute droplet-action snapshot your-droplet-id --snapshot-name "video-gen-backup-$(date +%Y%m%d)"
```

For data backups, consider mounting a Digital Ocean Volume for persistent storage. 
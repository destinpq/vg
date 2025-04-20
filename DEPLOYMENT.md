# Deployment Guide for the Video Generation Application

This guide provides instructions for deploying the AI Video Generation application on Digital Ocean.

## System Requirements

The Mochi-1 model requires significant resources for optimal performance:

- **Memory**: At least 16GB RAM
- **CPU**: 4+ CPU cores
- **GPU**: For production use, a GPU is highly recommended
- **Storage**: At least 50GB SSD storage for the application, models, and generated videos

## Recommended Digital Ocean Plan

Based on your application's needs (running Mochi-1 on your M4 Mac with 128GB unified memory), we recommend the following Digital Ocean options:

### For Development/Testing:

**Basic Droplet with CPU:**
- Premium CPU-Optimized Droplet: 8 vCPUs, 16GB RAM
- Plan: `c-8`
- Cost: $168/month
- Notes: Suitable for testing the application, but video generation will be slow without a GPU

### For Production (Preferred):

**GPU Droplet:**
- Basic GPU Droplet with NVIDIA A10G (24GB VRAM)
- Plan: `g-8vcpu-a10g`
- 8 vCPUs, 32GB RAM, 400GB SSD
- Cost: ~$520/month
- Notes: This provides comparable or better performance to your M4 Mac for AI model inference

## Deployment Steps

1. **Create the Droplet:**
   - Log in to Digital Ocean
   - Create a new Droplet with the recommended specifications
   - Select Ubuntu 22.04 LTS as the operating system

2. **Initial Server Setup:**
   ```bash
   # Update the system
   sudo apt update && sudo apt upgrade -y
   
   # Install required packages
   sudo apt install -y python3-pip python3-venv ffmpeg git
   
   # For GPU instances, install CUDA and cuDNN
   # Follow NVIDIA's official instructions for the specific Ubuntu version
   ```

3. **Clone the Repository:**
   ```bash
   git clone https://your-repository-url.git
   cd VideoGeneration
   ```

4. **Set Up Python Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   
   # Install backend requirements
   cd backend
   pip install -r requirements.txt
   
   # Install AI engine requirements
   cd ../models
   pip install -r requirements.txt
   
   # Install the model as a development package
   pip install -e .
   ```

5. **Configure the Application:**
   ```bash
   # Create environment files
   cd ../backend
   cp .env.example .env
   
   # Edit .env file to include your settings
   nano .env
   
   cd ../frontend
   cp .env.example .env
   
   # Edit frontend .env to point to your backend URL
   nano .env
   ```

6. **Build the Frontend:**
   ```bash
   cd ../frontend
   npm install
   npm run build
   ```

7. **Set Up a Production Server:**
   ```bash
   # Install PM2 for process management
   npm install -g pm2
   
   # Install nginx
   sudo apt install -y nginx
   
   # Configure nginx to serve the frontend and proxy API requests
   sudo nano /etc/nginx/sites-available/videogeneration
   ```
   
   Use the following nginx configuration:
   ```
   server {
       listen 80;
       server_name your-domain.com;
       
       # Frontend
       location / {
           root /path/to/VideoGeneration/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
       
       # Backend API
       location /api/ {
           proxy_pass http://localhost:8000/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       # Serve generated videos
       location /output/ {
           alias /path/to/VideoGeneration/backend/output/;
           add_header 'Access-Control-Allow-Origin' '*';
       }
   }
   ```

8. **Enable and Start the Services:**
   ```bash
   # Enable the nginx site
   sudo ln -s /etc/nginx/sites-available/videogeneration /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   
   # Start the backend with PM2
   cd /path/to/VideoGeneration/backend
   pm2 start "python main.py" --name "video-generation-backend"
   pm2 save
   pm2 startup
   ```

9. **Set Up HTTPS (Optional but Recommended):**
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Scaling Considerations

- **Storage**: As you generate more videos, monitor your disk usage and expand as needed
- **Memory**: The model requires significant RAM; consider upgrading if you see OOM errors
- **Multiple Users**: For handling multiple concurrent users, consider:
  - Using a load balancer with multiple backend instances
  - Implementing a job queue system (like Celery) for video generation tasks
  - Setting up a dedicated storage service for videos (like S3-compatible Spaces)

## Monitoring and Maintenance

- Set up monitoring with Digital Ocean's monitoring tools
- Regularly backup your database and generated videos
- Keep the system updated with security patches

## Cost Optimization

If the GPU droplet is too expensive for continuous operation:
- Consider using the droplet only when needed and shutting it down otherwise
- Use Digital Ocean's snapshot feature to save the state of your droplet
- Look into reserved instances for longer-term commitments at reduced prices

For more information, please refer to the [Digital Ocean Documentation](https://docs.digitalocean.com/) and the application's readme file. 
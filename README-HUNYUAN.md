# HunyuanVideo Docker Setup

This guide explains how to set up and run the Tencent HunyuanVideo model in Docker.

## Prerequisites

1. Docker installed and running
2. NVIDIA GPU with CUDA support
3. A Hugging Face account with access to [tencent/HunyuanVideo](https://huggingface.co/tencent/HunyuanVideo)

## H100 Setup for Digital Ocean

If you're using an NVIDIA H100 GPU on Digital Ocean, we've created a specialized configuration:

### 1. Create a Hugging Face Token

You need a Hugging Face token to download the model weights:

```bash
export HF_TOKEN=your_token_here
```

### 2. Run the H100 Deployment Script

The specialized script will configure everything for your H100 GPU:

```bash
chmod +x deploy-h100.sh
./deploy-h100.sh
```

This script:
- Verifies your H100 GPU is properly configured
- Creates the necessary directories
- Builds and runs the optimized Docker container
- Uses a configuration fine-tuned for H100 performance

### 3. Monitor the Logs

```bash
docker-compose -f docker-hunyuan-h100.yml logs -f
```

## Standard Setup

If you're not using an H100 GPU, follow these instructions instead:

### 1. Create a Hugging Face Token

You need a Hugging Face token to download the model weights:

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with read access
3. Export the token in your environment:

```bash
export HF_TOKEN=your_token_here
```

### 2. Prepare the Environment

Run the preparation script which will create necessary directories:

```bash
./prepare-hunyuan.sh
```

### 3. Build the Docker Container

```bash
docker-compose -f docker-hunyuan-gpu.yml build
```

### 4. Run the Container

```bash
docker-compose -f docker-hunyuan-gpu.yml up -d
```

The first time you run this, it will download the HunyuanVideo model weights which are several GB in size. The models will be saved to your local `./output/hunyuan-models` directory.

### 5. Check the Logs

```bash
docker-compose -f docker-hunyuan-gpu.yml logs -f
```

### 6. Access the API

The API will be available at `http://localhost:8000` once the model is loaded.

## Troubleshooting

### Error: Model Weights Not Found

If you see errors about missing model files, check:

1. Your HF_TOKEN is correctly set
2. You have access to the tencent/HunyuanVideo model on Hugging Face
3. You can manually trigger the download with:

```bash
docker-compose -f docker-hunyuan-gpu.yml run hunyuan-api python /root/hunyuan-models/download_weights.py --token $HF_TOKEN --output-dir /root/output/hunyuan-models
```

### Error: setup.py or pyproject.toml not found

If you see an error like "does not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found", this has been fixed in the latest Dockerfile. The Docker image now installs the required dependencies directly instead of relying on a setup.py file.

### Git Clone Error

If you see an error about the git clone failing because the directory already exists, you can clean up the container and build again:

```bash
docker-compose -f docker-hunyuan-gpu.yml down
docker-compose -f docker-hunyuan-gpu.yml build --no-cache
```

### Memory Issues

If you encounter memory issues, try:

1. Make sure USE_CPU_OFFLOAD=true is set in the docker-compose file
2. Consider using the FP8 quantized weights (see Hugging Face repository for details)

## Minimal Setup (Alternative)

If you're having issues with the standard setup, you can try the minimal version that doesn't rely on external Git repositories:

### 1. Prepare the minimal setup

```bash
# Use the same preparation script
./prepare-hunyuan.sh

# Copy minimal files to the right locations
cp hunyuan-docker/Dockerfile.minimal hunyuan-docker/Dockerfile
cp hunyuan-docker/entrypoint.minimal.sh hunyuan-docker/entrypoint.sh
cp hunyuan-docker/download_weights.minimal.py hunyuan-docker/download_weights.py
```

### 2. Build and run the minimal container

```bash
docker-compose -f docker-hunyuan-minimal.yml build
docker-compose -f docker-hunyuan-minimal.yml up -d
```

This minimal setup includes all necessary dependencies without attempting to clone any external repositories.

## Running Without NVIDIA GPU

If you're running on a system without an NVIDIA GPU, or having issues with NVIDIA drivers, you can use the CPU-only mode:

### Option 1: Use the CPU-only configuration

```bash
# Use the minimal setup first
./use-minimal-setup.sh

# Run with CPU-only configuration
docker-compose -f docker-hunyuan-cpu.yml build
docker-compose -f docker-hunyuan-cpu.yml up -d
```

### Option 2: Fix NVIDIA Driver Issues

If you have an NVIDIA GPU but are encountering driver issues, you might need to:

1. Install NVIDIA drivers on the host system
2. Install the NVIDIA Container Toolkit

For Ubuntu systems:

```bash
# Install NVIDIA drivers if needed
sudo apt-get update && sudo apt-get install -y nvidia-driver-510

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

Then try running with the GPU configuration again.

### Performance Expectations

Note that running in CPU-only mode will be significantly slower than with a GPU. Model loading and inference will take much longer, but it will work for testing purposes. 
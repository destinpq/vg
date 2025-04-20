# HunyuanVideo Docker Setup

This guide explains how to set up and run the Tencent HunyuanVideo model in Docker.

## Prerequisites

1. Docker installed and running
2. NVIDIA GPU with CUDA support
3. A Hugging Face account with access to [tencent/HunyuanVideo](https://huggingface.co/tencent/HunyuanVideo)

## Getting Started

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

This script will:
- Create the `output/hunyuan-models` directory where models will be stored
- Create a `.env` file for Docker Compose with your HF_TOKEN
- Check if HF_TOKEN is set

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
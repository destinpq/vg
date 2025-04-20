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

### 2. Build the Docker Container

```bash
# Use our helper script
./build-hunyuan.sh

# Or build directly with docker-compose
docker-compose -f docker-hunyuan-gpu.yml build
```

### 3. Run the Container

```bash
docker-compose -f docker-hunyuan-gpu.yml up -d
```

The first time you run this, it will download the HunyuanVideo model weights which are several GB in size.

### 4. Check the Logs

```bash
docker-compose -f docker-hunyuan-gpu.yml logs -f
```

### 5. Access the API

The API will be available at `http://localhost:8000` once the model is loaded.

## Troubleshooting

### Error: Model Weights Not Found

If you see errors about missing model files, check:

1. Your HF_TOKEN is correctly set
2. You have access to the tencent/HunyuanVideo model on Hugging Face
3. You can manually trigger the download with:

```bash
docker-compose -f docker-hunyuan-gpu.yml run hunyuan-api python /root/hunyuan-models/download_weights.py --token $HF_TOKEN
```

### Memory Issues

If you encounter memory issues, try:

1. Make sure USE_CPU_OFFLOAD=true is set in the docker-compose file
2. Consider using the FP8 quantized weights (see Hugging Face repository for details) 
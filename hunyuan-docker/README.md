# Hunyuan Video Docker Setup

This directory contains files for building and running the Tencent Hunyuan Video model in Docker on an H100 GPU. The setup handles downloading the 40GB+ model weights and provides a Flask API for video generation.

## Prerequisites

- Docker and Docker Compose
- NVIDIA Container Toolkit
- At least 100GB of disk space for the container and model weights
- H100 GPU with 80GB VRAM

## Quick Start

1. Create a `.env` file in the root directory (next to the `docker-hunyuan-gpu.yml` file) with your Hugging Face token (if needed):

```bash
# .env
HF_TOKEN=your_huggingface_token_here  # Optional, only if the model is gated
```

2. Build and start the container:

```bash
docker-compose -f docker-hunyuan-gpu.yml up -d
```

3. The first run will:
   - Build the Docker container
   - Download the Hunyuan Video model weights (~40GB)
   - Start the API server on port 8000

4. Check the logs to monitor the download and initialization:

```bash
docker-compose -f docker-hunyuan-gpu.yml logs -f
```

5. Test the API once it's running:

```bash
curl http://localhost:8000/health
```

## API Endpoints

### Health Check

```
GET /health
```

Returns information about the model and GPU status.

### Generate Video

```
POST /generate-video
```

Request body:

```json
{
  "prompt": "A cat walking in a garden, cinematic quality, 4K",
  "width": 576,
  "height": 320,
  "num_inference_steps": 50,
  "video_length": 129,
  "embedded_cfg_scale": 6.0,
  "seed": 42,
  "output_format": "gif"
}
```

All parameters except `prompt` are optional and have reasonable defaults.

## Data Persistence

The Docker setup uses volumes to persist:

- Model weights: Stored in a Docker volume to avoid downloading them again
- Generated videos: Stored in the `./output` directory which is mounted from the host

## Notes on Memory Usage

- The Hunyuan Video model requires significant VRAM (80GB H100 GPU recommended)
- The container uses CPU offloading to reduce VRAM usage when needed
- The container uses BF16 precision for optimal performance on H100

## Troubleshooting

### Driver/Library Version Mismatch

If you see `Failed to initialize NVML: Driver/library version mismatch`, make sure:

1. Your NVIDIA drivers are compatible with the CUDA version in the container
2. The NVIDIA Container Toolkit is properly installed
3. You may need to update your host's NVIDIA drivers

### Out of Memory Errors

If you encounter CUDA out of memory errors:

1. Try reducing the video resolution (width and height)
2. Reduce the number of inference steps
3. Make sure no other processes are using the GPU

## Integrating with Your Backend

Update your backend's `.env` file to point to the Hunyuan API:

```
HUNYUAN_API_URL=http://localhost:8000
```

Then restart your backend service to start using the Hunyuan Video model. 
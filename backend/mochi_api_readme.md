# Mochi-1 API Wrapper

This is a FastAPI wrapper for the Mochi-1 video generation model. It provides a simple REST API interface to the Mochi-1 CLI for generating videos from text prompts.

## Features

- Generate videos from text prompts
- Asynchronous video generation with job status tracking
- Fallback mode for testing without the actual Mochi-1 model
- Support for all Mochi-1 CLI parameters

## Setup

1. Ensure the Mochi-1 model weights are installed in the correct location (default: `models/weights`)
2. Install the required dependencies:
   ```bash
   pip install fastapi uvicorn opencv-python numpy
   ```

3. Start the API server:
   ```bash
   python mochi_api.py
   ```

The server will run on port 5001 by default.

## Environment Variables

- `MOCHI_MODEL_DIR`: Path to the Mochi-1 model weights (default: `models/weights`)
- `BASE_URL`: Base URL for accessing generated videos (default: `http://localhost:5001`)
- `USE_FALLBACK`: Set to "1" or "true" to use the fallback video generator (for testing without Mochi-1)

## API Endpoints

### Generate a Video

```
POST /generate
```

Request body:
```json
{
  "prompt": "A beautiful sunset over the ocean",
  "negative_prompt": "",
  "width": 848,
  "height": 480,
  "num_frames": 31,
  "seed": 12345,
  "cfg_scale": 6.0,
  "num_steps": 64
}
```

Response:
```json
{
  "video_id": "uuid-here",
  "prompt": "A beautiful sunset over the ocean",
  "video_url": "http://localhost:5001/outputs/video_uuid-here.mp4",
  "status": "processing"
}
```

### Check Video Generation Status

```
GET /status/{video_id}
```

Response:
```json
{
  "video_id": "uuid-here",
  "status": "completed",
  "prompt": "A beautiful sunset over the ocean",
  "video_url": "http://localhost:5001/outputs/video_uuid-here.mp4"
}
```

Status can be one of: `processing`, `completed`, `failed`

## Fallback Mode

If the Mochi-1 CLI is not available or you set `USE_FALLBACK=1`, the API will generate placeholder videos with the prompt text displayed. This is useful for testing the API without the actual Mochi-1 model.

## Files

- `mochi_api.py`: The main FastAPI application
- `outputs/`: Directory where generated videos are stored

## Example Usage with cURL

```bash
# Generate a video
curl -X POST http://localhost:5001/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful sunset over the ocean"}'

# Check status
curl http://localhost:5001/status/YOUR_VIDEO_ID
```

## Example Usage with Python

```python
import requests

# Generate a video
response = requests.post(
    "http://localhost:5001/generate",
    json={"prompt": "A beautiful sunset over the ocean"}
)
video_id = response.json()["video_id"]

# Check status
status_response = requests.get(f"http://localhost:5001/status/{video_id}")
print(status_response.json())
``` 
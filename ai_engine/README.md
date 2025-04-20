# HunyuanVideo Generator

An MVC-based application for generating high-quality videos from text prompts using Tencent's HunyuanVideo model, optimized for H100 GPUs.

## Features

- **1080p Video Generation**: Create high-quality Full HD videos from text descriptions
- **Load Balancing**: Handles multiple requests with a queue system
- **Performance Monitoring**: Real-time stats on GPU usage and generation times
- **Web Interface**: User-friendly UI for video generation
- **RESTful API**: Programmatic access to all features
- **Optimized for H100**: Takes full advantage of NVIDIA H100 GPUs

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hunyuanvideo-generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your paths
   ```

## Running the Service

### Standard Mode

```bash
python run.py --port 8080
```

### With Public Access (using ngrok)

```bash
python run_with_ngrok.py --port 8080
```

### Options

- `--port <PORT>`: Port to run the server on (default: 8080)
- `--host <HOST>`: Host to bind to (default: 0.0.0.0)
- `--debug`: Run in debug mode
- `--max-concurrent-jobs <N>`: Maximum number of concurrent generation jobs

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate` | POST | Generate a video from text |
| `/api/status/<id>` | GET | Get generation status |
| `/api/video/<id>` | GET | Download generated video |
| `/api/queue-status` | GET | View current queue status |
| `/api/stats` | GET | View generation statistics |
| `/api/gpu-status` | GET | View GPU information |
| `/api/resolutions` | GET | List supported resolutions |
| `/api/clean-old-videos` | POST | Clean up old videos |

## Supported Resolutions

- 1920x1080 (Full HD) - High quality
- 1280x720 (HD) - Good balance
- 960x544 (SD) - Faster generation
- 720x720 (Square) - For social media

## Project Structure

```
ai_engine/
├── controllers/    # API and generation controllers
├── models/         # Core model functionality
├── views/          # Web interface templates
├── utils/          # Helper utilities
├── config/         # Configuration settings
└── app.py          # Flask application
```

## Example API Usage

```python
import requests
import time

# Generate a video
response = requests.post(
    'http://localhost:8080/api/generate',
    json={
        "prompt": "A cat walks on the grass, realistic style.",
        "width": 1920,
        "height": 1080,
        "steps": 40,
        "use_fp8": True
    }
)
generation_id = response.json()['id']

# Check status until complete
while True:
    status_response = requests.get(f'http://localhost:8080/api/status/{generation_id}')
    status = status_response.json()['status']
    print(f"Status: {status}")
    
    if status in ['completed', 'failed']:
        break
    
    time.sleep(5)

# Download video (if completed)
if status == 'completed':
    video_url = f'http://localhost:8080/api/video/{generation_id}'
    print(f"Video available at: {video_url}")
``` 
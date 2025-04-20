# Lyrics to Video Backend

This service converts song lyrics into a video by generating a video prompt for each line using GPT-3.5 and then generating a video clip for each prompt using Mochi-1.

## Features

- Convert lyrics to video prompts using GPT-3.5 (with fallback)
- Generate video clips for each prompt using Mochi-1
- Stitch clips together to create a complete video
- Optional audio file support (URL or base64)
- Support for different languages and video styles

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

4. Start the service:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### `POST /lyrics/generate`

Generate a video from lyrics.

**Request Body:**
```json
{
  "lyrics": "Your lyrics here\nSplit into lines\nLike this",
  "language": "english",
  "style": "cinematic",
  "audio_file": "https://example.com/audio.mp3"  // or base64 encoded audio
}
```

**Response:**
```json
{
  "video_id": "uuid-here",
  "video_url": "http://localhost:8000/output/uuid-here/uuid-here.mp4",
  "lyrics": "Your lyrics here\nSplit into lines\nLike this",
  "clips": [],
  "prompts": [],
  "status": "processing"
}
```

### `GET /lyrics/status/{video_id}`

Check the status of a video generation job.

**Response:**
```json
{
  "video_id": "uuid-here",
  "video_url": "http://localhost:8000/output/uuid-here/uuid-here.mp4",
  "status": "completed",
  "lyrics": "Your lyrics here\nSplit into lines\nLike this",
  "clips": [
    "http://localhost:8000/output/uuid-here/clip_000.mp4",
    "http://localhost:8000/output/uuid-here/clip_001.mp4",
    "http://localhost:8000/output/uuid-here/clip_002.mp4"
  ],
  "prompts": [
    "A cinematic shot of...",
    "A beautiful scene showing...",
    "A dramatic sequence of..."
  ]
}
```

## Using the Lyrics to Prompts Utility

The backend includes a standalone utility to convert lyrics to video generation prompts. You can use this function directly in your Python code:

```python
# Asynchronous usage
from utils import generate_prompts_from_lyrics

async def process_lyrics():
    lyrics = "Line 1\nLine 2\nLine 3"
    prompts = await generate_prompts_from_lyrics(lyrics, language="english", style="cinematic")
    for prompt in prompts:
        print(f"Line: {prompt['line']}")
        print(f"Prompt: {prompt['prompt']}")

# Synchronous usage
from utils import generate_prompts_from_lyrics_sync

lyrics = "Line 1\nLine 2\nLine 3"
prompts = generate_prompts_from_lyrics_sync(lyrics, language="english", style="cinematic")
```

### Example Script

You can also use the included example script to convert lyrics to prompts interactively:

```bash
python examples/lyrics_to_prompts.py
```

This will prompt you to enter lyrics, language, and style information, then generate prompts for each line.

## Testing with the Mock Mochi Server

For testing purposes, a mock Mochi-1 service is included. This service generates placeholder videos instead of calling the actual Mochi-1 model.

Start the mock server:
```bash
python mock_mochi.py
```

This will start a server at http://localhost:5001 that responds to generation requests with simple videos displaying the prompt text.

## Running Tests

Run the tests with pytest:

```bash
pytest
```

Or run a specific test:

```bash
pytest tests/test_lyrics_to_prompts.py
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required for GPT prompt generation)
- `MOCHI_API_URL`: URL of the Mochi-1 service (default: http://localhost:5001)
- `OUTPUT_DIR`: Directory to store generated videos (default: ./output)
- `VIDEO_BASE_URL`: Base URL for accessing videos (default: http://localhost:8000/output)
- `FRONTEND_URL`: URL of the frontend for CORS (default: http://localhost:3000)

See the .env.example file for all available configuration options. 
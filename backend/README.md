# Video Generation API - Backend

A modern API for video generation using Hunyuan and other AI models. Built with FastAPI, Flask, and PostgreSQL.

## Features

- FastAPI for high-performance API endpoints
- Flask integration for backward compatibility
- PostgreSQL database for persistent storage
- Docker support
- Background task processing
- Hunyuan video generation integration
- Swagger documentation

## Requirements

- Python 3.9+
- PostgreSQL
- FFmpeg
- CUDA-capable GPU (optional)

## Installation

1. Clone the repository
2. Set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database
```bash
# Make sure PostgreSQL is running
psql -U postgres -c "CREATE DATABASE video_generation;"

# Run database migrations
alembic upgrade head
```

## Running the API

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 5001

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 5001
```

## API Endpoints

### FastAPI Endpoints

- `GET /api/hunyuan/health` - Check Hunyuan API status
- `POST /api/hunyuan/generate` - Generate a video with Hunyuan
- `GET /api/hunyuan/status/{video_id}` - Check video generation status
- `GET /api/hunyuan/videos` - List Hunyuan videos

Full API documentation is available at `/docs` when the server is running.

### Legacy Flask Endpoints

For backward compatibility, the following Flask endpoints are still available:

- `GET /flask/health` - Health check
- `GET /flask/hunyuan/status` - Check Hunyuan API status
- `POST /flask/hunyuan/generate` - Generate a video

## Database Structure

The API uses PostgreSQL for database storage with the following schema:

### Tables
- `users` - User accounts
- `videos` - Video metadata and status
- `lyric_prompts` - Lyrics and generated prompts
- `audio_analyses` - Audio analysis data

## Development

### Creating a Migration

```bash
# Generate a migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

### Running Tests

```bash
pytest
```

## Environment Variables

See `.env.example` for all available configuration options.

Required environment variables:
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_HOST` - PostgreSQL host
- `POSTGRES_PORT` - PostgreSQL port
- `POSTGRES_DB` - PostgreSQL database name
- `HUNYUAN_API_URL` - URL to the Hunyuan API

## Docker Support

The API can be run in Docker:

```bash
docker-compose up -d
``` 
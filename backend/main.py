import os
import asyncio # Import asyncio
from dotenv import load_dotenv
# Apply patches for numpy deprecation warnings and collections compatibility
# Previously needed for madmom, but now only using librosa for audio processing
from app.utils.patches import *

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from app.routes import video, lyrics, audio, upload
from app.utils.config import get_settings, verify_settings
from app.services.video_queue import video_queue # Import queue
from pathlib import Path
import re

# Load environment variables from .env file
load_dotenv()

# Explicitly set the OpenAI API key from environment
openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    print(f"OpenAI API key set from environment variables, length: {len(openai_api_key)}")
else:
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    openai_api_key = line.strip().split("=", 1)[1].strip()
                    # Remove quotes if present
                    if openai_api_key.startswith('"') and openai_api_key.endswith('"'):
                        openai_api_key = openai_api_key[1:-1]
                    elif openai_api_key.startswith("'") and openai_api_key.endswith("'"):
                        openai_api_key = openai_api_key[1:-1]
                    os.environ["OPENAI_API_KEY"] = openai_api_key
                    print(f"OpenAI API key loaded from .env file, length: {len(openai_api_key)}")
                    break
    except Exception as e:
        print(f"Error loading OpenAI API key from .env file: {e}")

# Load and verify settings
settings = get_settings()
verify_settings()

# Create output directory if it doesn't exist
output_dir = Path(settings.OUTPUT_DIR)
outputs_dir = Path("outputs")
os.makedirs(output_dir, exist_ok=True)
print(f"Static file serving from directory: {output_dir}")

async def lifespan(app: FastAPI):
    # Startup: Start the queue processor
    print("Application startup: Starting video queue processor...")
    await video_queue.start_processor()
    yield
    # Shutdown: Stop the queue processor
    print("Application shutdown: Stopping video queue processor...")
    await video_queue.stop_processor()
    print("Application shutdown complete.")

app = FastAPI(
    title="Video Generator API",
    description="API for generating videos from text and audio",
    version="1.0.0",
    lifespan=lifespan # Add lifespan context manager
)

# Get frontend URL from environment or use default
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
print(f"🔒 Configuring CORS for frontend at: {frontend_url}")

# Setup CORS with explicit frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],  # Explicitly allow the frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
)

# Serve static files from this directory
app.mount("/output", StaticFiles(directory=str(output_dir)), name="output")
# Also serve from outputs directory to handle both paths
if outputs_dir.exists() and outputs_dir != output_dir:
    print(f"Also serving static files from legacy directory: {outputs_dir}")
    app.mount("/outputs", StaticFiles(directory=str(outputs_dir)), name="outputs")

# Include routers
app.include_router(video.router, prefix="/video", tags=["Video Generation"])
app.include_router(lyrics.router, prefix="/lyrics", tags=["Lyrics Generation"])
app.include_router(audio.router, prefix="/audio", tags=["Audio Analysis"])
app.include_router(upload.router, prefix="/upload", tags=["File Upload"])

# Add a catch-all route for direct video file requests
@app.get("/{video_id:path}")
async def redirect_video_files(request: Request, video_id: str):
    # Check if this looks like a video file request (hunyuan_ID/filename.mp4)
    video_pattern = r'^(hunyuan_[a-zA-Z0-9_]+)(/.+)?$'
    match = re.match(video_pattern, video_id)
    
    if match:
        # This is a video ID request, redirect to the proper path
        video_id_part = match.group(1)
        file_part = match.group(2) or "/generated_video.mp4"  # Default to generated_video.mp4 if not specified
        
        # Check which directory exists
        output_path = Path(output_dir) / video_id_part
        outputs_path = Path(outputs_dir) / video_id_part
        
        if output_path.exists():
            # Redirect to /output/path
            return RedirectResponse(url=f"/output/{video_id_part}{file_part}")
        elif outputs_path.exists():
            # Redirect to /outputs/path
            return RedirectResponse(url=f"/outputs/{video_id_part}{file_part}")
    
    # Not a video request or video doesn't exist
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found", 
            "message": f"Resource not found: {video_id}",
            "documentation": "/docs"
        }
    )

@app.exception_handler(404)
async def custom_404_handler(request, exc):
    if request.url.path.startswith("/output/"):
        return JSONResponse(
            status_code=404,
            content={
                "error": "File not found",
                "message": "The requested video file is not available. It may still be processing or does not exist."
            }
        )
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"URL {request.url.path} not found",
            "documentation": "/docs"
        }
    )

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Video Generation API",
        "docs": "/docs",
        "endpoints": {
            "video": {
                "generate": "/video/generate",
                "status": "/video/status/{video_id}"
            },
            "lyrics": {
                "generate": "/lyrics/generate",
                "status": "/lyrics/status/{video_id}"
            },
            "audio": {
                "beats": "/audio/beats",
                "analyze": "/audio/analyze"
            }
        }
    }

# Error handler for our custom exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True) 
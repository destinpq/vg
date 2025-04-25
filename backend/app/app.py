"""
Main FastAPI application entry point.
This module creates and configures the FastAPI application.
"""

import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from pathlib import Path
import re

# Load environment variables and initialize application config
from app.config.settings import Settings, load_settings
from app.middleware.error_handlers import register_error_handlers
from app.middleware.request_logger import RequestLoggerMiddleware
from app.services.queue_service import video_queue
from app.services.database_service import db_service
from app.controllers import (
    video_controller,
    lyrics_controller, 
    audio_controller,
    upload_controller,
    hunyuan_controller,
    log_controller
)

# Load environment variables and initialize settings
load_dotenv()
settings = load_settings()

# Configure static file directories
output_dir = Path(settings.OUTPUT_DIR)
outputs_dir = Path("outputs")
os.makedirs(output_dir, exist_ok=True)

async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown tasks"""
    # Startup: Create database tables
    print("Application startup: Creating database tables...")
    await db_service.create_tables()
    
    # Startup: Start the queue processor
    print("Application startup: Starting video queue processor...")
    await video_queue.start_processor()
    
    yield
    
    # Shutdown: Stop the queue processor
    print("Application shutdown: Stopping video queue processor...")
    await video_queue.stop_processor()
    print("Application shutdown complete.")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Video Generator API",
        description="API for generating videos from text and audio",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add request logging middleware
    app.add_middleware(RequestLoggerMiddleware)
    
    # Configure CORS
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_url, "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Serve static files
    app.mount("/output", StaticFiles(directory=str(output_dir)), name="output")
    if outputs_dir.exists() and outputs_dir != output_dir:
        app.mount("/outputs", StaticFiles(directory=str(outputs_dir)), name="outputs")
    
    # Register all routers
    app.include_router(video_controller.router, prefix="/video", tags=["Video Generation"])
    app.include_router(lyrics_controller.router, prefix="/lyrics", tags=["Lyrics Generation"])
    app.include_router(audio_controller.router, prefix="/audio", tags=["Audio Analysis"])
    app.include_router(upload_controller.router, prefix="/upload", tags=["File Upload"])
    app.include_router(hunyuan_controller.router, prefix="/hunyuan", tags=["Hunyuan Video Generation"])
    app.include_router(log_controller.router, prefix="/logs", tags=["Activity Logs"])
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add direct video file requests handler
    @app.get("/{video_id:path}")
    async def redirect_video_files(request: Request, video_id: str):
        """Redirect to correct video file path based on video ID"""
        video_pattern = r'^(hunyuan_[a-zA-Z0-9_]+)(/.+)?$'
        match = re.match(video_pattern, video_id)
        
        if match:
            video_id_part = match.group(1)
            file_part = match.group(2) or "/generated_video.mp4"
            
            output_path = Path(output_dir) / video_id_part
            outputs_path = Path(outputs_dir) / video_id_part
            
            if output_path.exists():
                return RedirectResponse(url=f"/output/{video_id_part}{file_part}")
            elif outputs_path.exists():
                return RedirectResponse(url=f"/outputs/{video_id_part}{file_part}")
        
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "message": f"Resource not found: {video_id}"}
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """API root endpoint with documentation links"""
        return {
            "message": "Welcome to AI Video Generation API",
            "docs": "/docs",
            "endpoints": {
                "video": {"generate": "/video/generate", "status": "/video/status/{video_id}"},
                "lyrics": {"generate": "/lyrics/generate", "status": "/lyrics/status/{video_id}"},
                "audio": {"beats": "/audio/beats", "analyze": "/audio/analyze"},
                "hunyuan": {"status": "/hunyuan/status", "generate": "/hunyuan/generate"},
                "logs": {"browse": "/logs", "stats": "/logs/stats/overview"}
            }
        }
    
    return app

# Create application instance
app = create_app() 
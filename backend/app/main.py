from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Import database
from .db.database import engine, Base, get_db
from .db import models

# Import API routers
from .api.endpoints import hunyuan, videos, lyrics, users

# Import Flask app
from .flask_app import flask_app

# Load environment variables
load_dotenv()

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Video Generation API",
    description="API for video generation using Hunyuan and other models",
    version="1.0.0"
)

# Setup CORS
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory
output_dir = os.environ.get("OUTPUT_DIR", "output")
os.makedirs(output_dir, exist_ok=True)

# Mount static files
app.mount("/output", StaticFiles(directory=output_dir), name="output")

# Include API routers
app.include_router(hunyuan.router, prefix="/api/hunyuan", tags=["Hunyuan"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(lyrics.router, prefix="/api/lyrics", tags=["Lyrics"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

# Mount Flask app for backward compatibility
app.mount("/flask", WSGIMiddleware(flask_app))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Video Generation API",
        "docs": "/docs",
        "endpoints": {
            "hunyuan": {
                "health": "/api/hunyuan/health",
                "generate": "/api/hunyuan/generate",
                "status": "/api/hunyuan/status/{video_id}"
            },
            "videos": {
                "list": "/api/videos",
                "get": "/api/videos/{video_id}"
            },
            "lyrics": {
                "generate": "/api/lyrics/generate"
            },
            "users": {
                "me": "/api/users/me"
            }
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """API health check endpoint"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": str(e)}
        )

# Error handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"URL {request.url.path} not found",
            "documentation": "/docs"
        }
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc.detail) if hasattr(exc, 'detail') else "An unexpected error occurred"
        }
    )

# Run the application with uvicorn if the script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5001, reload=True) 
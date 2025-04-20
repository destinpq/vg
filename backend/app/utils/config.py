import os
import json
import warnings
from typing import List, Union, Optional, Dict, Any
from functools import lru_cache
from pathlib import Path
import torch

class Settings:
    """Simple settings class without using pydantic to avoid errors"""
    
    def __init__(self):
        # API Configuration
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self.API_V1_STR = "/api/v1"
        self.API_KEY = os.getenv("API_KEY", "")
        self.API_KEYS = []
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        
        # CORS Settings
        self.CORS_ORIGINS = ["*"]
        
        # Base paths
        self.BASE_DIR = Path(__file__).resolve().parent.parent.parent
        
        # Directories - ensure all paths are absolute and consistent
        self.ASSETS_DIR = self.BASE_DIR / "assets"
        self.OUTPUTS_DIR = self.BASE_DIR / "outputs"  # Keep this at backend/outputs for backward compatibility
        
        # Use consistent absolute paths for outputs
        output_dir = os.getenv("OUTPUT_DIR")
        if output_dir:
            self.OUTPUT_DIR = Path(output_dir).resolve()
        else:
            self.OUTPUT_DIR = self.OUTPUTS_DIR
            
        video_output_dir = os.getenv("VIDEO_OUTPUT_DIR")
        if video_output_dir:
            self.VIDEO_OUTPUT_DIR = Path(video_output_dir).resolve()
        else:
            self.VIDEO_OUTPUT_DIR = self.OUTPUT_DIR
            
        self.TEMP_DIR = self.BASE_DIR / "temp"
        
        # Model cache can be separately configured
        model_cache_dir = os.getenv("MODEL_CACHE_DIR")
        if model_cache_dir:
            self.MODEL_CACHE_DIR = Path(model_cache_dir).resolve()
        else:
            self.MODEL_CACHE_DIR = self.BASE_DIR / "model_cache"
        
        # Project Settings
        self.PROJECT_NAME = "HunyuanVideo Generator"
        
        # Video base URL
        self.VIDEO_BASE_URL = os.getenv("VIDEO_BASE_URL", "http://localhost:5001")
        
        # API URLs
        self.MOCHI_API_URL = os.getenv("MOCHI_API_URL", "https://api.mochi.video")
        self.REPLICATE_API_URL = os.getenv("REPLICATE_API_URL", "https://api.replicate.com")
        
        # API Keys
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        
        # GPU Configuration
        self.DEVICE = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
        self.CUDA_DEVICE = int(os.getenv("CUDA_DEVICE", "0"))
        self.ENABLE_MPS = os.getenv("ENABLE_MPS", "False").lower() == "true"
        
        # Video Generation
        self.DEFAULT_FPS = 30
        self.DEFAULT_DURATION = 5  # seconds
        self.DEFAULT_QUALITY = "standard"  # standard or high
        
        # Hunyuan Model Configuration
        self.HUNYUAN_MODEL_PATH = os.getenv("HUNYUAN_MODEL_PATH", "models/hunyuan_video")
        
        # Subtitle Configuration
        self.DEFAULT_SUBTITLE_STYLE = {
            "font": "Arial",
            "font_size": 30,
            "font_color": "white",
            "bg_color": "black",
            "bg_alpha": 0.5,
            "position": "bottom",
            "stroke_width": 1,
            "stroke_color": "black"
        }
        
        # Audio Configuration
        self.ENABLE_LIP_SYNC = False
        
        # Process API_KEYS
        if self.API_KEY:
            self.API_KEYS = [key.strip() for key in self.API_KEY.split(",")]
        
        # Ensure directories exist
        self.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        self.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.VIDEO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Ensure CUDA settings are correct
        if self.DEVICE == "cuda" and not torch.cuda.is_available():
            print("CUDA not available, falling back to CPU")
            self.DEVICE = "cpu"
    
    def verify_settings(self):
        """Verify that all required settings are properly configured"""
        if not Path(self.HUNYUAN_MODEL_PATH).exists():
            warnings.warn(f"Hunyuan model path does not exist: {self.HUNYUAN_MODEL_PATH}")
        
        print(f"Settings initialized. Using device: {self.DEVICE}")
        if self.DEVICE == "cuda":
            print(f"CUDA Device: {self.CUDA_DEVICE}")
        return True

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching
    
    Returns:
        Settings object with values from environment
    """
    settings = Settings()
    
    # Enable OpenAI integration if API key is available
    if settings.API_KEY and settings.API_KEY != "your_api_key_here":
        print("API key found. Enhanced functionality is available.")
    else:
        print("WARNING: API key not found. Some functionality may be limited.")
    
    return settings

def verify_settings() -> None:
    """
    Verify that critical settings are properly configured
    
    Raises:
        ValueError: If a critical setting is missing
    """
    settings = get_settings()
    
    # Create output directory if it doesn't exist
    output_dir = Path(settings.OUTPUTS_DIR).resolve()
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Verify API key
    if not settings.API_KEY:
        print("WARNING: API key is not set. Some functionality may be limited.")
    
    # Verify Hunyuan model path
    if not Path(settings.HUNYUAN_MODEL_PATH).exists():
        print(f"WARNING: Hunyuan model path does not exist: {settings.HUNYUAN_MODEL_PATH}")
    
    # Log the CORS settings
    origins = settings.CORS_ORIGINS
    print(f"CORS origins: {origins}")
    
    # Log video base URL for debugging
    base_url = f"http://localhost:{settings.API_PORT}/{settings.OUTPUTS_DIR}"
    print(f"Video base URL: {base_url}")
        
    # For future: Add any other setting validation here 
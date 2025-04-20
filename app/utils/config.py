import os
import json
# Removed pydantic import to avoid compatibility issues
from typing import List, Union, Dict, Any, Optional
from functools import lru_cache
from pathlib import Path

class Settings:
    """Application settings from environment variables"""
    
    def __init__(self):
        # Load environment variables from .env file if it exists
        self._load_env_file()
        
        # API Configuration
        self.API_HOST = os.environ.get("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.environ.get("API_PORT", "5001"))
        self.DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "t")
        
        # Added missing environment variables
        self.HOST = os.environ.get("HOST", "0.0.0.0")
        self.PORT = os.environ.get("PORT", "5555")  
        self.ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
        
        # CORS Configuration
        self.FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        cors_value = os.environ.get("CORS_ORIGINS", '["http://localhost:3000", "http://localhost:3000", "http://localhost:8080"]')
        try:
            self.CORS_ORIGINS = json.loads(cors_value) if cors_value.startswith("[") else cors_value.split(",")
        except:
            self.CORS_ORIGINS = ["http://localhost:3000", "http://localhost:3000", "http://localhost:8080"]
        
        # Directories
        self.OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "./output")
        self.MODEL_CACHE_DIR = os.environ.get("MODEL_CACHE_DIR", "./model_cache")
        self.AI_ENGINE_PATH = os.environ.get("AI_ENGINE_PATH", "./models/mochi-1")
        
        # GPU Configuration
        self.USE_GPU = os.environ.get("USE_GPU", "True").lower() in ("true", "1", "t")
        self.CUDA_DEVICE = int(os.environ.get("CUDA_DEVICE", "0"))
        self.HALF_PRECISION = os.environ.get("HALF_PRECISION", "True").lower() in ("true", "1", "t")
        
        # Service URLs
        self.VIDEO_BASE_URL = os.environ.get("VIDEO_BASE_URL", "http://localhost:5001/output")
        self.MOCHI_API_URL = os.environ.get("MOCHI_API_URL", "http://localhost:5001")
        
        # API Keys
        self.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        self.PIKA_API_KEY = os.environ.get("PIKA_API_KEY", "")
        self.REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
        
        # Model Configuration
        self.MODEL_NAME = os.environ.get("MODEL_NAME", "stabilityai/stable-diffusion-xl-base-1.0")
        
        # Hunyuan Configuration
        self.hunyuan_model_version = os.environ.get("HUNYUAN_MODEL_VERSION", "latest")
        
        # Queue Configuration
        self.MAX_QUEUE_SIZE = int(os.environ.get("MAX_QUEUE_SIZE", "5"))
        
        # Video generation settings
        self.DEFAULT_FPS = int(os.environ.get("DEFAULT_FPS", "24"))
        self.DEFAULT_DURATION = int(os.environ.get("DEFAULT_DURATION", "5"))
        self.MAX_DURATION = int(os.environ.get("MAX_DURATION", "30"))
        self.PREVIEW_DURATION = int(os.environ.get("PREVIEW_DURATION", "3"))
        
        # OpenAI API for creative prompt enhancement
        self.USE_OPENAI = os.environ.get("USE_OPENAI", "False").lower() in ("true", "1", "t")
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if not os.environ.get(key):
                        os.environ[key] = value

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS into a list regardless of input format"""
        if isinstance(self.CORS_ORIGINS, str):
            # Handle JSON string
            if self.CORS_ORIGINS.startswith("[") and self.CORS_ORIGINS.endswith("]"):
                try:
                    return json.loads(self.CORS_ORIGINS)
                except json.JSONDecodeError:
                    pass
            # Handle comma-separated string
            if "," in self.CORS_ORIGINS:
                return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
            # Handle single origin
            return [self.CORS_ORIGINS]
        # Already a list
        return self.CORS_ORIGINS

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching
    
    Returns:
        Settings object with values from environment
    """
    settings = Settings()
    
    # Enable OpenAI integration if API key is available
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
        settings.USE_OPENAI = True
        print("OpenAI integration enabled")
    else:
        settings.USE_OPENAI = False
        print("OpenAI integration disabled - API key not found")
    
    return settings

def verify_settings() -> None:
    """
    Verify that critical settings are properly configured
    
    Raises:
        ValueError: If a critical setting is missing
    """
    settings = get_settings()
    
    # Create output directory if it doesn't exist
    output_dir = Path(settings.OUTPUT_DIR).resolve()
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Verify OpenAI API key if needed
    if not settings.OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY is not set. Fallback prompt generation will be used.")
    
    # Verify Replicate API key for realistic human generation
    if not settings.REPLICATE_API_TOKEN:
        print("WARNING: REPLICATE_API_TOKEN is not set. Realistic human generation will be limited.")
        print("For best results with human subjects, please set REPLICATE_API_TOKEN in your .env file.")
    else:
        print("✅ Replicate API key found. Enhanced realistic human generation is available.")
    
    # Log the CORS settings
    origins = settings.cors_origins_list
    print(f"CORS origins: {origins}")
    
    # Log video base URL for debugging
    base_url = f"http://localhost:5555/{settings.OUTPUT_DIR}"
    print(f"Video base URL: {base_url}")
        
    # For future: Add any other setting validation here 
"""
Application settings and configuration.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings model"""
    # API Configuration
    API_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=True)
    
    # File storage settings
    OUTPUT_DIR: str = Field(default="output")
    UPLOAD_DIR: str = Field(default="uploads")
    
    # OpenAI settings
    OPENAI_API_KEY: str = Field(default="")
    
    # Hunyuan API settings
    HUNYUAN_API_URL: str = Field(default="http://localhost:8000")
    
    # Database settings
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/video_generation")
    
    # Frontend URL
    FRONTEND_URL: str = Field(default="http://localhost:3000")
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

def load_settings() -> Settings:
    """Load and validate settings"""
    # Explicitly set the OpenAI API key from environment if available
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # Check for the Hunyuan API URL
    hunyuan_api_url = os.environ.get("HUNYUAN_API_URL")
    if not hunyuan_api_url:
        os.environ["HUNYUAN_API_URL"] = "http://localhost:8000"
    
    # Create output directory if it doesn't exist
    settings = Settings()
    output_dir = Path(settings.OUTPUT_DIR)
    upload_dir = Path(settings.UPLOAD_DIR)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)
    
    return settings

# Export singleton settings instance
settings = load_settings() 
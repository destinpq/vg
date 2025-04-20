from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union

class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""
    prompt: str = Field(..., description="Text prompt describing the video to generate")
    duration: float = Field(5.0, description="Video duration in seconds (max 30s)")
    fps: int = Field(24, description="Frames per second")
    quality: str = Field("high", description="Quality setting (low, medium, high)")
    style: str = Field("realistic", description="Video style (abstract, realistic)")
    subtitles: Optional[List[Dict[str, Any]]] = Field(None, description="Optional subtitles to add to the video")
    enable_lip_sync: bool = Field(False, description="Whether to enable lip sync if subtitles are provided")
    subtitle_style: Optional[Dict[str, Any]] = Field(None, description="Style options for subtitles")

class VideoGenerationResponse(BaseModel):
    """Response model for video generation request."""
    id: str = Field(..., description="Unique identifier for the video generation task")
    status: str = Field(..., description="Current status of the task (queued, processing, completed, failed)")
    message: str = Field(..., description="Human-readable message about the task status")
    
class VideoGenerationStatus(BaseModel):
    """Status model for video generation."""
    id: str = Field(..., description="Unique identifier for the video generation task")
    status: str = Field(..., description="Current status of the task (queued, processing, completed, failed)")
    progress: float = Field(0, description="Progress percentage from 0 to 100")
    message: str = Field("", description="Human-readable message about the task status")
    url: Optional[str] = Field(None, description="URL to the generated video if completed")

class SubtitleEntry(BaseModel):
    """Model for a single subtitle entry."""
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Subtitle text")
    
class SubtitleStyle(BaseModel):
    """Model for subtitle styling options."""
    font_size: int = Field(24, description="Font size")
    font_color: str = Field("white", description="Font color")
    background: bool = Field(True, description="Whether to show a background")
    background_color: str = Field("black", description="Background color")
    background_opacity: float = Field(0.5, description="Background opacity (0-1)")
    position: tuple = Field(("center", "bottom"), description="Position (horizontal, vertical)") 
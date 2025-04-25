"""
Lyrics schema models for request/response validation.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Union, List, Dict, Any

class LyricsToVideoRequest(BaseModel):
    """Schema for lyrics to video request."""
    lyrics: str = Field(..., description="Lyrics to convert to a video")
    language: str = Field("english", description="Language of the lyrics")
    style: Optional[str] = Field(None, description="Style of the video to generate")
    audio_file: Optional[Union[str, HttpUrl]] = Field(None, description="Audio file or URL")

class VideoGenerationPrompt(BaseModel):
    """Schema for video generation prompt."""
    prompt: str = Field(..., description="Prompt for the video generation")
    line: str = Field(..., description="Original lyrics line")
    index: int = Field(..., description="Index of the line in the original lyrics")

class LyricsToVideoResponse(BaseModel):
    """Schema for lyrics to video response."""
    video_id: str = Field(..., description="Unique identifier for the generated video")
    video_url: Optional[str] = Field(None, description="URL to access the generated video")
    lyrics: str = Field(..., description="Original lyrics used for generation")
    clips: Optional[List[str]] = Field(None, description="List of clip URLs for each line")
    prompts: List[Dict[str, Any]] = Field(..., description="List of prompts used for each clip")
    status: str = Field(..., description="Status of the video generation")

class LyricsGenerationRequest(BaseModel):
    """Schema for lyrics generation request."""
    text: str = Field(..., description="Text to generate lyrics prompts for")
    language: str = Field("english", description="Language of the text")
    style: Optional[str] = Field(None, description="Style of prompts to generate")

class LyricsModel(BaseModel):
    """Serializable model for Lyrics database model."""
    id: str
    original_text: str
    language: str
    status: str
    style: Optional[str] = None
    prompts: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    
    class Config:
        orm_mode = True 
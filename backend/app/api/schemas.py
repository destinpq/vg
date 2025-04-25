from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Video schemas
class VideoBase(BaseModel):
    title: str = Field(..., description="Title of the video")
    description: Optional[str] = Field(None, description="Description of the video")
    prompt: str = Field(..., description="Text prompt for video generation")

class VideoCreateHunyuan(VideoBase):
    width: int = Field(576, description="Video width in pixels")
    height: int = Field(320, description="Video height in pixels")
    num_inference_steps: int = Field(50, description="Number of inference steps")
    output_format: str = Field("mp4", description="Output format (mp4 or gif)")

class VideoCreateMochi(VideoBase):
    duration: float = Field(5.0, description="Video duration in seconds")
    fps: int = Field(24, description="Frames per second")
    quality: str = Field("standard", description="Video quality")
    style: str = Field("realistic", description="Video style")

class VideoResponse(BaseModel):
    id: int
    video_id: str
    title: str
    description: Optional[str]
    prompt: str
    status: str
    model_type: str
    file_path: Optional[str]
    thumbnail_path: Optional[str]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class VideoStatus(BaseModel):
    video_id: str
    status: str
    progress: float = Field(0.0, description="Progress from 0 to 100")
    message: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

# Lyrics schemas
class LyricsRequest(BaseModel):
    lyrics: str
    num_prompts: int = Field(5, description="Number of prompts to generate")

class LyricsResponse(BaseModel):
    video_id: str
    lyrics: str
    prompts: List[Dict[str, Any]]
    message: str

# Audio schemas
class AudioAnalysisRequest(BaseModel):
    audio_file: str
    
class AudioAnalysisResponse(BaseModel):
    video_id: str
    beats: List[float]
    tempo: float
    segments: List[Dict[str, Any]] 
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Union, List

class LyricsToVideoRequest(BaseModel):
    """
    Schema for lyrics to video request
    """
    lyrics: str = Field(..., description="Lyrics to convert to a video")
    language: str = Field(..., description="Language of the lyrics")
    style: Optional[str] = Field(None, description="Style of the video to generate")
    audio_file: Optional[Union[str, HttpUrl]] = Field(None, description="Base64 encoded audio or URL to an audio file")

class VideoGenerationPrompt(BaseModel):
    """
    Schema for video generation prompt
    """
    prompt: str = Field(..., description="Prompt for the video generation")
    line: str = Field(..., description="Original lyrics line")
    index: int = Field(..., description="Index of the line in the original lyrics")

class LyricsToVideoResponse(BaseModel):
    """
    Schema for lyrics to video response
    """
    video_id: str = Field(..., description="Unique identifier for the generated video")
    video_url: str = Field(..., description="URL to access the generated video")
    lyrics: str = Field(..., description="Original lyrics used for generation")
    clips: List[str] = Field(..., description="List of clip URLs for each line")
    prompts: List[str] = Field(..., description="List of prompts used for each clip")
    status: str = Field(..., description="Status of the video generation") 
"""
Utility functions - kept for backward compatibility.

These functions are now implemented in appropriate services as part of our MVC structure.
This module keeps them for backward compatibility with existing code.
"""
import logging
from typing import List, Dict, Any, Optional

from ..services.lyrics_service import lyrics_service
from ..services.video_service import VideoService
from ..services.database_service import db_service

# Configure logging
logger = logging.getLogger(__name__)

# Create a video service instance
video_service = VideoService(db_service)

# Re-export the functions and constants
HINDI_EXAMPLES = lyrics_service.HINDI_EXAMPLES

# Lyrics functions
async def generate_prompts_from_lyrics(lyrics: str, language: str = "english", style: Optional[str] = None) -> List[Dict[str, Any]]:
    """Forward to lyrics_service.generate_prompts_from_lyrics"""
    return await lyrics_service.generate_prompts_from_lyrics(lyrics, language, style)

def generate_prompts_from_lyrics_sync(lyrics: str, language: str = "english", style: Optional[str] = None) -> List[Dict[str, Any]]:
    """Forward to lyrics_service.generate_prompts_from_lyrics_sync"""
    return lyrics_service.generate_prompts_from_lyrics_sync(lyrics, language, style)

# Video functions
def stitch_videos(video_paths: List[str], output_path: str) -> str:
    """Forward to video_service.stitch_videos"""
    return video_service.stitch_videos(video_paths, output_path)

async def stitch_videos_async(video_paths: List[str], output_path: str) -> str:
    """Forward to video_service.stitch_videos_async"""
    return await video_service.stitch_videos_async(video_paths, output_path) 
"""
Schema module for Pydantic request/response models.
"""
from .video import (
    VideoGenerationRequest, VideoGenerationResponse, VideoGenerationStatus,
    SubtitleEntry, SubtitleStyle, VideoModel
)
from .lyrics import (
    LyricsToVideoRequest, VideoGenerationPrompt, LyricsToVideoResponse,
    LyricsGenerationRequest, LyricsModel
)
from .hunyuan import (
    HunyuanGenerationRequest, HunyuanGenerationResponse, HunyuanStatusResponse
)
from .activity_log import (
    ActivityLogCreate, ActivityLogResponse
)

__all__ = [
    "VideoGenerationRequest", "VideoGenerationResponse", "VideoGenerationStatus",
    "SubtitleEntry", "SubtitleStyle", "VideoModel",
    "LyricsToVideoRequest", "VideoGenerationPrompt", "LyricsToVideoResponse",
    "LyricsGenerationRequest", "LyricsModel",
    "HunyuanGenerationRequest", "HunyuanGenerationResponse", "HunyuanStatusResponse",
    "ActivityLogCreate", "ActivityLogResponse"
] 
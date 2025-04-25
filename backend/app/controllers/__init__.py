"""
Controllers module for API endpoints and routes.
"""
from . import (
    video_controller,
    lyrics_controller,
    audio_controller,
    upload_controller,
    hunyuan_controller,
    log_controller
)

__all__ = [
    "video_controller",
    "lyrics_controller",
    "audio_controller",
    "upload_controller",
    "hunyuan_controller",
    "log_controller"
] 
"""
AI Core module - Implementation of GPU-accelerated video generation
"""

import os
import sys
import time
import subprocess
import re  # Add explicit import for regular expressions
from pathlib import Path
import torch
import numpy as np
import cv2
import asyncio
import replicate
import httpx
import logging
import requests
from typing import Union, List, Optional, Dict, Any, Tuple, Callable, Awaitable
from backend.app.utils.config import get_settings
from backend.app.utils.file_utils import ensure_directory
from backend.app.utils.gpu_info import get_gpu_info, get_gpu_acceleration_info
# Import the HunyuanVideoGenerator
from backend.app.models.hunyuan.hunyuan_video import HunyuanVideoGenerator

# Setup logging
logger = logging.getLogger(__name__)

# Load settings instance
settings = get_settings()

print("="*50)
print("SYSTEM DIAGNOSTICS:")
print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")
if torch.cuda.is_available():
    print(f"CUDA available: True")
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    print(f"✅ Using GPU for Hunyuan video generation")
    DEVICE = torch.device("cuda")
    
    # Configure CUDA for optimal performance
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
else:
    print(f"CUDA available: False")
    print(f"⚠️ Using CPU for video generation (much slower)")
    DEVICE = torch.device("cpu")
print("="*50)

def preprocess_prompt(prompt: str) -> str:
    """
    Preprocess the prompt for video generation
    """
    # Basic preprocessing
    cleaned_prompt = prompt.strip()
    
    # Convert to lowercase
    cleaned_prompt = cleaned_prompt.lower()
    
    # Remove multiple spaces
    cleaned_prompt = re.sub(r'\s+', ' ', cleaned_prompt)
    
    # Add video-specific enhancers if not present
    video_keywords = ["cinematic", "dynamic", "motion", "scene", "video"]
    
    has_video_keyword = any(keyword in cleaned_prompt for keyword in video_keywords)
    if not has_video_keyword:
        cleaned_prompt = f"cinematic video of {cleaned_prompt}"
    
    # Add quality enhancers if not present
    quality_keywords = ["high quality", "detailed", "4k", "HD", "sharp"]
    
    has_quality_keyword = any(keyword in cleaned_prompt.lower() for keyword in quality_keywords)
    if not has_quality_keyword:
        cleaned_prompt = f"{cleaned_prompt}, high quality, detailed"
    
    return cleaned_prompt.strip()

def extract_prompt_attributes(prompt: str) -> Dict[str, Any]:
    """
    Extract attributes from the prompt for targeted generation
    """
    attributes = {
        "style": None,
        "lighting": None,
        "camera_movement": None,
        "environment": None,
        "time_of_day": None,
        "colors": [],
        "subject": None,
        "mood": None,
        "weather": None,
        "category": None,
    }
    
    # Define categories with related keywords
    categories = {
        "nature": ["forest", "mountain", "tree", "flower", "garden", "plant", "jungle", "woods", "waterfall", "lake", "river", "nature"],
        "ocean": ["sea", "ocean", "beach", "water", "wave", "underwater", "marine", "coastal", "shore", "sand", "island", "tropical"],
        "sky": ["sky", "cloud", "star", "night sky", "constellation", "meteor", "comet", "galaxy", "universe", "space", "planet", "cosmic"],
        "urban": ["city", "street", "building", "skyline", "urban", "architecture", "downtown", "metropolis", "skyscraper", "town", "village"],
        "weather": ["rain", "storm", "lightning", "thunderstorm", "snow", "winter", "foggy", "misty", "cloudy", "windy", "tornado", "hurricane"],
        "abstract": ["abstract", "pattern", "fractal", "geometric", "surreal", "psychedelic", "vibrant", "colorful", "neon", "glow", "distortion"],
        "fantasy": ["fantasy", "magical", "mystical", "fairy", "dragon", "castle", "medieval", "enchanted", "mythical", "legend", "elf", "unicorn"],
        "animals": ["animal", "dog", "cat", "bird", "wildlife", "lion", "tiger", "eagle", "fish", "wolf", "bear", "elephant", "horse"],
        "portrait": ["portrait", "face", "person", "woman", "man", "child", "girl", "boy", "people", "human", "figure", "silhouette"],
    }
    
    # Determine the primary category of the prompt
    for category, keywords in categories.items():
        if any(keyword in prompt.lower() for keyword in keywords):
            attributes["category"] = category
            for keyword in keywords:
                if keyword in prompt.lower():
                    attributes["subject"] = keyword
                    break
            break
    
    # Extract style
    style_patterns = [
        r'(cinematic|anime|cartoon|photorealistic|3d|abstract|noir|vintage|realistic|artistic)',
        r'in the style of (\w+)',
    ]
    for pattern in style_patterns:
        style_match = re.search(pattern, prompt, re.IGNORECASE)
        if style_match:
            attributes["style"] = style_match.group(1).lower()
            break
    
    # Extract time of day
    time_patterns = [
        r'(morning|afternoon|evening|night|dawn|dusk|sunset|sunrise)',
    ]
    for pattern in time_patterns:
        time_match = re.search(pattern, prompt, re.IGNORECASE)
        if time_match:
            attributes["time_of_day"] = time_match.group(1).lower()
            break
    
    # Extract mood
    mood_keywords = ["happy", "sad", "peaceful", "exciting", "dramatic", "mysterious", "romantic", "scary", "creepy", "tranquil", "serene"]
    for mood in mood_keywords:
        if mood in prompt.lower():
            attributes["mood"] = mood
            break
    
    # Extract weather
    weather_keywords = ["rainy", "sunny", "cloudy", "stormy", "foggy", "snowy", "windy", "clear"]
    for weather in weather_keywords:
        if weather in prompt.lower():
            attributes["weather"] = weather
            break
    
    # Extract colors
    color_patterns = [
        r'(red|blue|green|yellow|purple|pink|orange|black|white|violet|indigo|cyan|magenta|gold|silver|brown)',
    ]
    colors_found = []
    for match in re.finditer(color_patterns[0], prompt, re.IGNORECASE):
        colors_found.append(match.group(1).lower())
    if colors_found:
        attributes["colors"] = colors_found
    
    return attributes

def add_subtitles_to_video(video_path, subtitles, subtitle_style):
    """
    Add subtitles to a video file
    
    Args:
        video_path: Path to the video file
        subtitles: List of SubtitleEntry objects
        subtitle_style: Dictionary containing style options
    
    Returns:
        Path to the video with subtitles
    """
    import moviepy.editor as mp
    from moviepy.video.tools.subtitles import SubtitlesClip
    import os
    
    logger.info(f"Adding subtitles to video: {video_path}")
    
    # Create output path for subtitled video
    filename, ext = os.path.splitext(video_path)
    output_path = f"{filename}_subtitled{ext}"
    
    # Load the video
    video = mp.VideoFileClip(video_path)
    
    # Convert subtitles to the format expected by moviepy
    subs = []
    for sub in subtitles:
        subs.append(((sub["start"], sub["end"]), sub["text"]))
    
    # Create subtitles clip
    font_size = subtitle_style.get("font_size", 24)
    font_color = subtitle_style.get("font_color", "white")
    
    generator = lambda txt: mp.TextClip(
        txt, 
        font='Arial', 
        fontsize=font_size, 
        color=font_color,
        bg_color=subtitle_style.get("background_color", "black") if subtitle_style.get("background", True) else None,
        size=(video.w, None),
        method='caption'
    )
    
    if subtitle_style.get("background", True):
        generator = lambda txt: mp.TextClip(
            txt, 
            font='Arial', 
            fontsize=font_size, 
            color=font_color,
            bg_color=subtitle_style.get("background_color", "black"),
            size=(video.w, None),
            method='caption'
        ).set_opacity(subtitle_style.get("background_opacity", 0.5))
    
    subtitles_clip = SubtitlesClip(subs, generator)
    
    # Position the subtitles
    position = lambda t: ('center', 'bottom')
    subtitles_clip = subtitles_clip.set_position(position)
    
    # Composite video with subtitles
    final_video = mp.CompositeVideoClip([video, subtitles_clip])
    
    # Write output
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    logger.info(f"Subtitles added successfully: {output_path}")
    return output_path

def apply_lip_sync(video_path, audio_path, subtitles):
    """
    Apply lip sync to a video using the audio and subtitles for timing
        
    Args:
        video_path: Path to the video file
        audio_path: Path to the audio file
        subtitles: List of SubtitleEntry objects for timing
            
    Returns:
        Path to the video with lip sync applied
    """
    import os
    from datetime import datetime
    import subprocess
    
    logger.info(f"Applying lip sync to video: {video_path}")
    
    # This is where you would integrate with a lip sync library like Wav2Lip
    # For now, we'll implement a simplified version that just overlays audio
    
    # Create output path
    filename, ext = os.path.splitext(video_path)
    output_path = f"{filename}_lipsync{ext}"
    
    try:
        # For a complete implementation, you would use a model like Wav2Lip
        # Here we'll just combine the video with the audio
        command = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            output_path
        ]
        
        subprocess.run(command, check=True)
        logger.info(f"Lip sync (audio overlay) applied successfully: {output_path}")
        
        # Note for production: Replace with actual lip sync implementation
        # TODO: Implement full lip sync with Wav2Lip or similar technology
        logger.warning("Using simplified audio overlay instead of true lip sync - requires additional implementation")
        
        return output_path
    except Exception as e:
        logger.error(f"Error applying lip sync: {str(e)}")
        return video_path

class HunyuanWrapper:
    """A wrapper class for the Hunyuan GPU-accelerated video generation."""

    def __init__(self, settings=None):
        """Initialize the Hunyuan wrapper with the given settings."""
        self.settings = settings or get_settings()
        self.logger = logging.getLogger("ai_core.HunyuanWrapper")
        self.hunyuan_generator = None
        self.is_initialized = False

    async def initialize(self):
        """Initialize and load the Hunyuan video generator."""
        if self.is_initialized:
            return
            
        try:
            self.logger.info("Initializing Hunyuan video generator...")
            self.hunyuan_generator = HunyuanVideoGenerator(self.settings.MODEL_CACHE_DIR)
            
            # Setup the environment and load models
            await self.hunyuan_generator.setup_environment()
            await self.hunyuan_generator.load_model()
            
            self.is_initialized = True
            self.logger.info("Hunyuan video generator initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize Hunyuan video generator: {str(e)}")
            raise

    async def generate_video(self, video_request: dict, progress_callback: Optional[Callable] = None) -> str:
        """
        Generate a video based on the given request using Hunyuan.
        
        Args:
            video_request: A dictionary containing:
                - id: Job ID
                - prompt: The text prompt for video generation
                - duration: The desired video duration in seconds
                - fps: Frames per second
                - quality: Quality setting (low, medium, high)
                - style: Video style (abstract, realistic)
                - subtitles: Optional list of subtitle entries
                - enable_lip_sync: Whether to enable lip sync
                - subtitle_style: Style options for subtitles
            progress_callback: Optional callback function for progress updates
                
        Returns:
            The path to the generated video file.
        """
        # Ensure the generator is initialized
        if not self.is_initialized:
            await self.initialize()
            
        # Extract request parameters
        job_id = video_request.get("id", f"job_{int(time.time())}")
        prompt = video_request.get("prompt", "")
        duration = video_request.get("duration", 5.0)
        fps = video_request.get("fps", 24)
        quality = video_request.get("quality", "high")
        style = video_request.get("style", "realistic")
        subtitles = video_request.get("subtitles", None)
        enable_lip_sync = video_request.get("enable_lip_sync", False)
        subtitle_style = video_request.get("subtitle_style", None)
        
        # Process the prompt to get required attributes for video generation
        processed_prompt, attributes = self._extract_video_attributes(prompt, duration, fps, quality, style)
        
        # Create job-specific output directory that matches the URL pattern
        output_dir = Path(self.settings.OUTPUT_DIR) / job_id
        ensure_directory(output_dir)
        
        # Use the expected filename from the route handler
        output_filename = "generated_video.mp4"
        output_path = output_dir / output_filename
        
        try:
            # Convert duration to number of frames based on FPS
            video_length = int(duration * fps)
            
            # Map quality settings to generation parameters
            quality_settings = {
                "low": {"video_size": (480, 640), "steps": 30},
                "medium": {"video_size": (720, 1280), "steps": 40},
                "high": {"video_size": (1080, 1920), "steps": 50}
            }
            
            # Get generation parameters based on quality
            gen_params = quality_settings.get(quality.lower(), quality_settings["medium"])
            
            # Generate the video using Hunyuan
            self.logger.info(f"Generating video with Hunyuan using prompt: {processed_prompt}")
            
            # Progress tracking callback wrapper
            async def _progress_callback(percent, message):
                if progress_callback:
                    await progress_callback(percent, message)
            
            # Generate the video
            video_path = await self.hunyuan_generator.generate_video(
                prompt=processed_prompt,
                output_path=output_path,
                video_size=gen_params["video_size"],
                video_length=video_length,
                steps=gen_params["steps"],
                progress_callback=_progress_callback
            )
            
            # Apply subtitles if provided
            if subtitles and len(subtitles) > 0:
                self.logger.info(f"Adding subtitles to video: {video_path}")
                video_path = add_subtitles_to_video(video_path, subtitles, subtitle_style)
                
                # Apply lip sync if requested and subtitles are available
                if enable_lip_sync:
                    # For lip sync, we would need an audio file
                    # This is a placeholder - a real implementation would need an audio file to sync with
                    # audio_path = "path_to_audio_file.wav"  # This should be provided or generated
                    # video_path = apply_lip_sync(video_path, audio_path, subtitles)
                    self.logger.warning("Lip sync requested but not implemented yet")
            
            return str(video_path)
        except Exception as e:
            self.logger.error(f"Error generating video: {str(e)}")
            raise

    def _extract_video_attributes(self, prompt, default_duration, default_fps, default_quality, default_style):
        """
        Extract video generation attributes from the prompt.
            
        Returns:
            tuple: (processed_prompt, attributes_dict)
        """
        attributes = {
            "duration": default_duration,
            "fps": default_fps,
            "quality": default_quality,
            "style": default_style
        }
        
        # Process the prompt to extract any specific attributes
        processed_prompt = preprocess_prompt(prompt)
        extracted_attrs = extract_prompt_attributes(prompt)
        
        # Update attributes with extracted values
        if extracted_attrs:
            for key, value in extracted_attrs.items():
                if key in attributes and value is not None:
                    attributes[key] = value
        
        return processed_prompt, attributes 
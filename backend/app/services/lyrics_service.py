import os
import sys
import uuid
import base64
import asyncio
import httpx
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import json
import logging
from openai import AsyncOpenAI
import aiofiles
import ffmpeg
import requests
from urllib.parse import urlparse
from datetime import datetime

from app.utils.config import get_settings
from app.utils.utils import stitch_videos_async
from app.services.log_service import log_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample Hindi-to-English prompt translations as examples
HINDI_EXAMPLES = {
    "Main tujhe chaand laake dunga": "A man under a moonlit sky holding a gift box in his hands.",
    "Tere naam se zindagi ik nayi si ho gayi hai": "A person looking hopeful as the sunrise bathes their face in warm golden light.",
    "Jab tak hai jaan": "A couple walking hand in hand along a beach at sunset, silhouetted against the horizon.",
    "Meri raaton ko chain nahi aata": "A person lying awake in bed, moonlight streaming through the window as they stare at the ceiling.",
    "Pyaar hame kis mod pe le aaya": "Two people standing at a crossroads in a picturesque landscape, looking uncertain but hopeful."
}

class LyricsService:
    """
    Service for converting lyrics to videos
    """
    def __init__(self):
        self.settings = get_settings()
        self.output_dir = Path(self.settings.OUTPUT_DIR)
        self.base_url = self.settings.VIDEO_BASE_URL
        self.mochi_api_url = self.settings.MOCHI_API_URL
        self.openai_api_key = self.settings.OPENAI_API_KEY
        self.active_jobs: Dict[str, Any] = {}
        
        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize OpenAI client
        self.openai_client = AsyncOpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        
    async def generate_prompts_from_lyrics(self, lyrics: str, language: str = "english", style: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate cinematic scene descriptions from song lyrics.
        
        Args:
            lyrics: Multi-line song lyrics
            language: Language of the lyrics (default: "english")
            style: Optional style for the generated prompts (e.g., "cinematic", "animated")
            
        Returns:
            List of dictionaries with prompt data:
            [
                {"prompt": "A cinematic scene...", "line": "Original lyrics line", "index": 0},
                ...
            ]
        """
        # Start timing for logging
        start_time = datetime.utcnow()
        
        # Split lyrics into lines
        lyrics_lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        # Log the lyrics processing request
        log_entry = await log_service.log_activity({
            "endpoint": "lyrics/generate_prompts",
            "method": "POST",
            "path": "/lyrics/generate_prompts",
            "start_time": start_time,
            "request_data": {
                "lyrics": lyrics,
                "language": language,
                "style": style
            },
            "metadata": {
                "num_lines": len(lyrics_lines),
                "language": language,
                "operation_type": "lyrics_to_prompts"
            }
        })
        
        # If no lines, return empty list
        if not lyrics_lines:
            # Log empty result
            if log_entry:
                await log_service.log_response(
                    log_entry,
                    200,
                    response_data={"prompts": [], "message": "No lyrics lines found"}
                )
            return []
        
        prompts = []
        
        # Prepare style instruction
        style_instruction = f" in {style} style" if style else ""
        
        # Prepare system prompt for OpenAI
        system_prompt = (
            f"You are a creative video director. Convert each line of lyrics in {language} "
            f"into a detailed, visual prompt that can be used to generate video clips{style_instruction}. "
            f"The prompt should be visually descriptive and capture the emotion and meaning of the lyrics."
        )
        
        try:
            for i, line in enumerate(lyrics_lines):
                # If no OpenAI client or for Hindi examples, use fallback/example mappings
                if not self.openai_client or (language.lower() == "hindi" and line in HINDI_EXAMPLES):
                    if language.lower() == "hindi" and line in HINDI_EXAMPLES:
                        # Use predefined examples for Hindi lyrics
                        prompt = HINDI_EXAMPLES[line]
                    else:
                        # Fallback simple prompt generation
                        prompt = f"A cinematic scene showing {line}"
                        if style:
                            prompt += f" in {style} style"
                    
                    prompts.append({
                        "prompt": prompt,
                        "line": line,
                        "index": i
                    })
                    continue
                
                try:
                    # Real OpenAI API call
                    response = await self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Lyrics line: {line}"}
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )
                    
                    # Extract the prompt from the response
                    prompt = response.choices[0].message.content.strip()
                    
                    prompts.append({
                        "prompt": prompt,
                        "line": line,
                        "index": i
                    })
                    
                    # Be nice to API rate limits
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error generating prompt for line {i}: {e}")
                    # Fallback
                    prompt = f"A cinematic scene showing {line}"
                    if style:
                        prompt += f" in {style} style"
                        
                    prompts.append({
                        "prompt": prompt,
                        "line": line,
                        "index": i
                    })
            
            # Calculate processing time
            end_time = datetime.utcnow()
            processing_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Log successful response
            if log_entry:
                await log_service.log_response(
                    log_entry,
                    200,
                    response_data={
                        "prompts": prompts,
                        "count": len(prompts),
                        "processing_time_ms": processing_time_ms
                    }
                )
                
            return prompts
            
        except Exception as e:
            logger.error(f"Error generating prompts from lyrics: {e}")
            
            # Log error
            if log_entry:
                await log_service.log_response(
                    log_entry,
                    500,
                    error=str(e)
                )
                
            # Return empty list on error
            return []
    
    def generate_prompts_from_lyrics_sync(self, lyrics: str, language: str = "english", style: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Synchronous version of generate_prompts_from_lyrics
        """
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run the async function in the loop
            return loop.run_until_complete(self.generate_prompts_from_lyrics(lyrics, language, style))
        finally:
            # Close the loop
            loop.close()
    
    async def generate_video_from_lyrics(
        self, 
        lyrics: str, 
        language: str, 
        style: Optional[str] = None, 
        audio_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a video based on the provided lyrics
        """
        # Create unique ID for this job
        job_id = str(uuid.uuid4())
        job_dir = self.output_dir / job_id
        os.makedirs(job_dir, exist_ok=True)
        
        # Record job information
        self.active_jobs[job_id] = {
            "id": job_id,
            "status": "processing",
            "lyrics": lyrics,
            "language": language,
            "style": style,
            "clips": [],
            "prompts": [],
            "output_path": job_dir / f"{job_id}.mp4"
        }
        
        # Start processing in the background
        asyncio.create_task(self._process_lyrics_to_video(job_id, lyrics, language, style, audio_file))
        
        # Return response with job information
        return {
            "video_id": job_id,
            "video_url": f"{self.base_url}/{job_id}/{job_id}.mp4",
            "lyrics": lyrics,
            "clips": [],
            "prompts": [],
            "status": "processing"
        }
    
    async def _process_lyrics_to_video(
        self, 
        job_id: str, 
        lyrics: str, 
        language: str, 
        style: Optional[str] = None,
        audio_file: Optional[str] = None
    ):
        """
        Process lyrics to video in the background
        """
        try:
            job = self.active_jobs[job_id]
            job_dir = self.output_dir / job_id
            
            # 1. Split lyrics into lines
            lyrics_lines = self._split_lyrics(lyrics)
            
            # 2. Generate video prompts for each line using GPT
            prompts = await self.generate_prompts_from_lyrics(lyrics, language, style)
            job["prompts"] = [p["prompt"] for p in prompts]
            
            # 3. Generate video clips for each prompt
            clip_paths = []
            for i, prompt_data in enumerate(prompts):
                clip_path = job_dir / f"clip_{i:03d}.mp4"
                await self._generate_clip(prompt_data["prompt"], clip_path)
                clip_paths.append(clip_path)
                job["clips"].append(f"{self.base_url}/{job_id}/clip_{i:03d}.mp4")
            
            # 4. Process audio file if provided
            audio_path = None
            if audio_file:
                audio_path = await self._process_audio(audio_file, job_dir)
            
            # 5. Stitch clips together
            output_path = job_dir / f"{job_id}.mp4"
            await self._stitch_clips(clip_paths, output_path, audio_path)
            
            # Update job status
            job["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Error in video generation: {e}")
            if job_id in self.active_jobs:
                self.active_jobs[job_id]["status"] = "failed"
                self.active_jobs[job_id]["error"] = str(e)
    
    def _split_lyrics(self, lyrics: str) -> List[str]:
        """
        Split lyrics into individual lines
        """
        # Remove empty lines and strip whitespace
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        return lines
    
    async def _generate_clip(self, prompt: str, output_path: Path) -> Path:
        """
        Generate a video clip based on the provided prompt
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Call the Mochi service
                response = await client.post(
                    f"{self.mochi_api_url}/generate",
                    json={"prompt": prompt}
                )
                
                if response.status_code != 200:
                    logger.error(f"Error from Mochi service: {response.text}")
                    raise Exception(f"Failed to generate clip: {response.text}")
                
                # For demo purposes, if Mochi service isn't available, create a placeholder
                if "video_data" not in response.json():
                    logger.warning("No video data in response. Creating placeholder.")
                    return await self._create_placeholder_clip(prompt, output_path)
                
                # Save the video data
                video_data = base64.b64decode(response.json()["video_data"])
                async with aiofiles.open(output_path, "wb") as f:
                    await f.write(video_data)
                
                return output_path
        except Exception as e:
            logger.error(f"Error generating clip: {e}")
            # Create a placeholder clip as fallback
            return await self._create_placeholder_clip(prompt, output_path)
    
    async def _create_placeholder_clip(self, prompt: str, output_path: Path) -> Path:
        """
        Create a placeholder clip with text (for demo/fallback purposes)
        """
        import cv2
        import numpy as np
        
        # Create a simple text video (5 seconds at 24fps)
        width, height = 640, 360
        fps = 24
        duration = 5  # seconds
        
        # Create a temporary directory for individual frames
        with tempfile.TemporaryDirectory() as temp_dir:
            frames_dir = Path(temp_dir)
            
            # Generate frames
            for i in range(duration * fps):
                # Create a frame with text
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Add a gradient background
                for y in range(height):
                    for x in range(width):
                        frame[y, x] = [
                            int(100 + 50 * np.sin(i / (fps * 2) + x / 100)),
                            int(100 + 50 * np.cos(i / (fps * 2) + y / 100)),
                            int(150 + 50 * np.sin(i / (fps * 2) + (x+y) / 200))
                        ]
                
                # Add the prompt text, wrapped to fit on screen
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.7
                font_color = (255, 255, 255)
                line_type = 2
                
                # Simple text wrapping
                words = prompt.split()
                lines = []
                current_line = ""
                max_width = width - 40
                
                for word in words:
                    test_line = current_line + word + " "
                    text_size = cv2.getTextSize(test_line, font, font_scale, line_type)[0]
                    
                    if text_size[0] > max_width:
                        lines.append(current_line)
                        current_line = word + " "
                    else:
                        current_line = test_line
                        
                if current_line:
                    lines.append(current_line)
                
                # Draw each line
                y_position = height // 2 - (len(lines) * 30) // 2
                for line in lines:
                    text_size = cv2.getTextSize(line, font, font_scale, line_type)[0]
                    x_position = (width - text_size[0]) // 2
                    
                    # Add text shadow for better readability
                    cv2.putText(
                        frame, line, (x_position + 2, y_position + 2), 
                        font, font_scale, (0, 0, 0), line_type
                    )
                    
                    cv2.putText(
                        frame, line, (x_position, y_position), 
                        font, font_scale, font_color, line_type
                    )
                    
                    y_position += 30
                
                # Save the frame
                frame_path = frames_dir / f"frame_{i:04d}.jpg"
                cv2.imwrite(str(frame_path), frame)
            
            # Use ffmpeg to create a video from the frames
            (
                ffmpeg
                .input(f"{frames_dir}/frame_%04d.jpg", framerate=fps)
                .output(str(output_path), vcodec='libx264', pix_fmt='yuv420p')
                .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            )
            
        return output_path
    
    async def _process_audio(self, audio_file: str, job_dir: Path) -> Optional[Path]:
        """
        Process the provided audio file (URL or base64)
        """
        audio_path = job_dir / "audio.mp3"
        
        try:
            # Check if it's a URL
            parsed_url = urlparse(audio_file)
            if parsed_url.scheme and parsed_url.netloc:
                # Download the audio file
                async with httpx.AsyncClient() as client:
                    response = await client.get(audio_file)
                    if response.status_code == 200:
                        async with aiofiles.open(audio_path, "wb") as f:
                            await f.write(response.content)
                        return audio_path
                    else:
                        logger.error(f"Failed to download audio: {response.status_code}")
                        return None
            else:
                # Assume it's base64 encoded
                try:
                    # Try to decode as base64
                    audio_data = base64.b64decode(audio_file)
                    async with aiofiles.open(audio_path, "wb") as f:
                        await f.write(audio_data)
                    return audio_path
                except Exception as e:
                    logger.error(f"Failed to decode audio data: {e}")
                    return None
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return None
    
    async def _stitch_clips(
        self, 
        clip_paths: List[Path], 
        output_path: Path,
        audio_path: Optional[Path] = None
    ) -> Path:
        """
        Stitch multiple video clips together and optionally add audio
        """
        if not clip_paths:
            raise ValueError("No clips to stitch together")
        
        # Convert Path objects to strings for stitch_videos function
        clip_paths_str = [str(path) for path in clip_paths]
        
        # First stitch videos without audio
        if audio_path:
            # If we need to add audio, use a temporary file first
            temp_output = output_path.with_suffix(".temp.mp4")
            await stitch_videos_async(clip_paths_str, str(temp_output))
            
            # Then add audio
            try:
                (
                    ffmpeg
                    .input(str(temp_output))
                    .input(str(audio_path))
                    .output(
                        str(output_path), 
                        codec="copy", 
                        acodec="aac", 
                        strict="experimental", 
                        shortest=None
                    )
                    .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                )
                
                # Remove temporary file
                os.remove(temp_output)
            except Exception as e:
                # If adding audio fails, just use the video without audio
                logger.error(f"Error adding audio to stitched video: {e}")
                if os.path.exists(temp_output):
                    os.rename(temp_output, output_path)
        else:
            # No audio, just stitch the videos
            await stitch_videos_async(clip_paths_str, str(output_path))
            
        return output_path
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a job
        """
        if job_id not in self.active_jobs:
            return {"status": "not_found"}
        
        job = self.active_jobs[job_id]
        return {
            "video_id": job_id,
            "video_url": f"{self.base_url}/{job_id}/{job_id}.mp4" if job["status"] == "completed" else None,
            "status": job["status"],
            "lyrics": job["lyrics"],
            "clips": job["clips"],
            "prompts": job["prompts"]
        }

# Create singleton instance
lyrics_service = LyricsService() 
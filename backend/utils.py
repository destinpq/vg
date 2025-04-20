import os
import logging
import asyncio
import subprocess
import tempfile
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from openai import AsyncOpenAI
from app.utils.config import get_settings

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

async def generate_prompts_from_lyrics(lyrics: str, language: str = "english", style: Optional[str] = None) -> List[Dict[str, Any]]:
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
    # Get settings to access OpenAI API key
    settings = get_settings()
    openai_api_key = settings.OPENAI_API_KEY
    
    # Split lyrics into lines
    lyrics_lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
    if not lyrics_lines:
        return []
    
    prompts = []
    
    # Create OpenAI client if API key is available
    openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
    
    # Prepare style instruction
    style_instruction = f" in {style} style" if style else ""
    
    # Prepare system prompt for OpenAI
    system_prompt = (
        f"You are a creative video director. Convert each line of lyrics in {language} "
        f"into a detailed, visual prompt that can be used to generate video clips{style_instruction}. "
        f"The prompt should be visually descriptive and capture the emotion and meaning of the lyrics."
    )
    
    for i, line in enumerate(lyrics_lines):
        # If no OpenAI API key or for Hindi examples, use fallback/example mappings
        if not openai_client or (language.lower() == "hindi" and line in HINDI_EXAMPLES):
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
            response = await openai_client.chat.completions.create(
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
    
    return prompts

# Synchronous version that can be called directly without async
def generate_prompts_from_lyrics_sync(lyrics: str, language: str = "english", style: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Synchronous version of generate_prompts_from_lyrics
    """
    import asyncio
    
    # Create new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Run the async function in the loop
        return loop.run_until_complete(generate_prompts_from_lyrics(lyrics, language, style))
    finally:
        # Close the loop
        loop.close()

def stitch_videos(video_paths: List[str], output_path: str) -> str:
    """
    Stitch multiple videos together using ffmpeg.
    
    This function concatenates videos with the same resolution and frame rate.
    It uses a concat demuxer through an intermediate file list.
    
    Args:
        video_paths: List of paths to video files to stitch together
        output_path: Path where the stitched video will be saved
    
    Returns:
        Path to the stitched video file
    
    Raises:
        ValueError: If the video list is empty or if videos have different resolutions/frame rates
        subprocess.CalledProcessError: If ffmpeg command fails
        OSError: If file operations fail
    """
    if not video_paths:
        raise ValueError("No videos provided to stitch")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Check that all videos exist
    for path in video_paths:
        if not os.path.exists(path):
            raise ValueError(f"Video file not found: {path}")
    
    # Verify that all videos have the same resolution and frame rate
    if len(video_paths) > 1:
        # Get information about the first video
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-of", "json", video_paths[0]
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        first_video_info = json.loads(result.stdout)
        
        try:
            first_width = first_video_info["streams"][0]["width"]
            first_height = first_video_info["streams"][0]["height"]
            first_frame_rate = first_video_info["streams"][0]["r_frame_rate"]
        except (KeyError, IndexError) as e:
            raise ValueError(f"Could not parse video info for {video_paths[0]}: {e}")
        
        # Check all other videos
        for path in video_paths[1:]:
            cmd = [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate",
                "-of", "json", path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            video_info = json.loads(result.stdout)
            
            try:
                width = video_info["streams"][0]["width"]
                height = video_info["streams"][0]["height"]
                frame_rate = video_info["streams"][0]["r_frame_rate"]
            except (KeyError, IndexError) as e:
                raise ValueError(f"Could not parse video info for {path}: {e}")
            
            if width != first_width or height != first_height:
                raise ValueError(
                    f"Video resolution mismatch: {path} has {width}x{height}, "
                    f"but first video has {first_width}x{first_height}"
                )
            
            if frame_rate != first_frame_rate:
                raise ValueError(
                    f"Video frame rate mismatch: {path} has {frame_rate} fps, "
                    f"but first video has {first_frame_rate} fps"
                )
    
    # Create a temporary file with the list of videos to concatenate
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        concat_list_path = f.name
        for video_path in video_paths:
            # Use absolute paths to avoid issues with paths containing spaces
            abs_path = os.path.abspath(video_path)
            # Escape single quotes in the path
            safe_path = abs_path.replace("'", "\\'")
            f.write(f"file '{safe_path}'\n")
    
    try:
        # Build the ffmpeg command
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c", "copy",
            output_path
        ]
        
        # Run the ffmpeg command
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Verify that the output file exists and has size > 0
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise ValueError(f"Failed to create stitched video: {output_path}")
        
        return output_path
    
    finally:
        # Clean up the temporary file
        if os.path.exists(concat_list_path):
            os.remove(concat_list_path)

# Async version of stitch_videos
async def stitch_videos_async(video_paths: List[str], output_path: str) -> str:
    """
    Asynchronous version of stitch_videos
    
    Args:
        video_paths: List of paths to video files to stitch together
        output_path: Path where the stitched video will be saved
    
    Returns:
        Path to the stitched video file
    """
    # Run the synchronous function in a thread pool executor
    return await asyncio.to_thread(stitch_videos, video_paths, output_path) 
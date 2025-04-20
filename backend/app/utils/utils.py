"""
Utility functions for the backend app
"""

import os
import sys
import asyncio
import subprocess
from typing import List, Dict, Any, Union
from pathlib import Path
import time
import uuid
import json

# Instead of importing, let's define the function here directly
# This avoids conflicts with ai_engine.utils

async def stitch_videos_async(video_files, output_file, temp_dir=None):
    """
    Asynchronously stitch multiple video files together
    
    Args:
        video_files: List of video file paths
        output_file: Path to save the stitched video
        temp_dir: Optional temporary directory for intermediate files
    
    Returns:
        Path to the output file
    """
    if not video_files:
        raise ValueError("No video files provided")
    
    # Create a temporary file list
    list_file = Path(temp_dir or os.path.dirname(output_file)) / f"filelist_{uuid.uuid4()}.txt"
    
    with open(list_file, "w") as f:
        for video in video_files:
            f.write(f"file '{Path(video).absolute()}'\n")
    
    # Create FFmpeg command
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_file)
    ]
    
    # Run the command asynchronously
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    # Clean up
    if os.path.exists(list_file):
        os.remove(list_file)
    
    if process.returncode != 0:
        raise Exception(f"Error stitching videos: {stderr.decode()}")
    
    return output_file

# Add more utility functions as needed 
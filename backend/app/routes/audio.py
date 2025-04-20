from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from typing import Dict, Any, List
import shutil

from ..utils.audio.beat_detector import get_beat_timestamps, analyze_beats

router = APIRouter(prefix="/audio", tags=["audio"])


@router.post("/beats")
async def detect_beats(file: UploadFile = File(...)) -> Dict[str, List[float]]:
    """
    Detect beats in an uploaded audio file and return timestamps.
    
    Args:
        file: Uploaded audio file
        
    Returns:
        Dictionary with beat timestamps in seconds
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith(("audio/", "video/")):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Create a temporary file to save the uploaded audio
    temp_dir = tempfile.mkdtemp()
    try:
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get beat timestamps
        beat_times = get_beat_timestamps(temp_file_path)
        
        return {"beat_timestamps": beat_times}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting beats: {str(e)}")
    
    finally:
        # Clean up temporary files
        shutil.rmtree(temp_dir)


@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Perform comprehensive beat analysis on an uploaded audio file.
    
    Args:
        file: Uploaded audio file
        
    Returns:
        Dictionary with beat analysis results
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith(("audio/", "video/")):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Create a temporary file to save the uploaded audio
    temp_dir = tempfile.mkdtemp()
    try:
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get comprehensive beat analysis
        analysis = analyze_beats(temp_file_path)
        
        # Ensure all values are JSON serializable
        for key, value in analysis.items():
            if hasattr(value, 'tolist'):
                analysis[key] = value.tolist()
                
        return analysis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing audio: {str(e)}")
    
    finally:
        # Clean up temporary files
        shutil.rmtree(temp_dir) 
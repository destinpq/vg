"""
Beat Detection Module

This module provides functionality to detect beats in audio files using librosa.
It includes different algorithms for beat detection and returns timestamps for each detected beat.
"""

import os
import numpy as np
from typing import List, Optional, Dict, Any, Tuple, Union

# Import librosa for audio processing
import librosa

def get_beat_timestamps(audio_path: str) -> List[float]:
    """
    Extract beat timestamps from an audio file using librosa.
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        List[float]: List of beat timestamps in seconds
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    return get_beats_librosa(audio_path)

def get_beats_librosa(audio_path: str) -> List[float]:
    """
    Extract beat timestamps using librosa.
    
    This function uses librosa's beat tracking algorithm, which is based on 
    dynamic programming and tempo estimation.
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        List[float]: List of beat timestamps in seconds
    """
    # Load the audio file
    y, sr = librosa.load(audio_path, sr=None)
    
    # Extract tempo and beat frames
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    
    # Convert beat frames to timestamps
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    return beat_times.tolist()

def get_downbeats(audio_path: str) -> List[float]:
    """
    Simplified downbeat detection (every 4 beats).
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        List[float]: List of estimated downbeat timestamps in seconds
    """
    # Get beats
    beats = get_beats_librosa(audio_path)
    
    # Assume 4/4 time signature (most common) - take every 4th beat
    downbeats = [beats[i] for i in range(0, len(beats), 4)]
    
    return downbeats

def analyze_beats(audio_path: str) -> Dict[str, Any]:
    """
    Perform a comprehensive beat analysis of an audio file.
    
    Returns various metrics including:
    - Beat timestamps
    - Downbeat timestamps
    - Tempo (BPM)
    - Beat intervals
    - Beat regularity scores
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        Dict[str, Any]: Dictionary with beat analysis results
    """
    # Get basic beat timestamps
    beat_times = get_beat_timestamps(audio_path)
    
    # Get simple downbeats (every 4 beats)
    downbeat_times = get_downbeats(audio_path)
    
    # Calculate intervals between beats
    beat_intervals = np.diff(beat_times).tolist() if len(beat_times) > 1 else []
    
    # Calculate average tempo (BPM)
    if beat_intervals:
        avg_beat_interval = np.mean(beat_intervals)
        bpm = 60.0 / avg_beat_interval
    else:
        bpm = 0
    
    # Measure beat regularity (lower std dev = more regular)
    beat_regularity = np.std(beat_intervals) if len(beat_intervals) > 1 else 0
    
    return {
        "beat_timestamps": beat_times,
        "downbeat_timestamps": downbeat_times,
        "tempo_bpm": bpm,
        "beat_intervals": beat_intervals,
        "beat_regularity": beat_regularity,
        "total_beats": len(beat_times)
    }

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python beat_detector.py <audio_file_path>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    print(f"Analyzing beats for: {audio_file}")
    
    try:
        beat_times = get_beat_timestamps(audio_file)
        print(f"Found {len(beat_times)} beats.")
        print(f"First 5 beat timestamps: {beat_times[:5]}")
        
        # Get more detailed analysis
        analysis = analyze_beats(audio_file)
        print(f"Tempo: {analysis['tempo_bpm']:.1f} BPM")
        print(f"Beat regularity: {analysis['beat_regularity']:.4f} (lower = more regular)")
        
        if analysis['downbeat_timestamps']:
            print(f"Found {len(analysis['downbeat_timestamps'])} downbeats (first beats of measures)")
        
    except Exception as e:
        print(f"Error analyzing beats: {e}")
        sys.exit(1) 
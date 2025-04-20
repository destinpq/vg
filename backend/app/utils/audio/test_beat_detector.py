#!/usr/bin/env python3
"""
Test script for the beat detector module.

Usage:
    python test_beat_detector.py <audio_file_path>
"""

import os
import sys
import time
from typing import List
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.utils.audio.beat_detector import get_beat_timestamps, analyze_beats


def print_beats(beats: List[float], max_display: int = 10) -> None:
    """Pretty print beat timestamps"""
    if not beats:
        print("No beats detected.")
        return
    
    print(f"Total beats detected: {len(beats)}")
    display_count = min(max_display, len(beats))
    
    print(f"First {display_count} beats (seconds):")
    for i, beat in enumerate(beats[:display_count]):
        print(f"  {i+1}. {beat:.3f}s")
    
    if len(beats) > max_display:
        print(f"  ... {len(beats) - max_display} more beats")


def test_beat_detection(audio_path: str) -> None:
    """Run different beat detection methods and compare results"""
    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}")
        return
    
    print(f"\nAnalyzing audio file: {audio_path}")
    print("-" * 50)
    
    # Test basic beat detection
    print("\n1. Basic Beat Detection:")
    start_time = time.time()
    beats = get_beat_timestamps(audio_path)
    duration = time.time() - start_time
    
    print_beats(beats)
    print(f"Detection time: {duration:.2f} seconds")
    
    # Test comprehensive analysis
    print("\n2. Comprehensive Beat Analysis:")
    start_time = time.time()
    analysis = analyze_beats(audio_path)
    duration = time.time() - start_time
    
    print(f"Analysis time: {duration:.2f} seconds")
    print(f"Tempo: {analysis['tempo_bpm']:.1f} BPM")
    print(f"Beat regularity: {analysis['beat_regularity']:.4f} (lower = more regular)")
    print(f"Total beats: {analysis['total_beats']}")
    
    if analysis['downbeat_timestamps']:
        print(f"Downbeats detected: {len(analysis['downbeat_timestamps'])}")
        print("First few downbeats (seconds):")
        for i, beat in enumerate(analysis['downbeat_timestamps'][:5]):
            print(f"  {i+1}. {beat:.3f}s")
    
    # Save analysis to JSON file
    output_path = os.path.splitext(audio_path)[0] + "_beat_analysis.json"
    with open(output_path, 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        serializable_analysis = {k: v for k, v in analysis.items()}
        json.dump(serializable_analysis, f, indent=2)
    
    print(f"\nAnalysis saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_beat_detector.py <audio_file_path>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    test_beat_detection(audio_file) 
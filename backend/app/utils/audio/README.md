# Audio Beat Detection Module

This module provides functionality to detect and analyze beats in audio files using both `librosa` and `madmom` libraries. It includes different algorithms for beat detection and returns timestamps for each detected beat.

## Features

- **Beat Detection**: Get precise timestamps of beats in audio files
- **Downbeat Detection**: Identify the first beat of each measure (useful for musical phrase detection)
- **Tempo Estimation**: Calculate BPM (Beats Per Minute) of audio
- **Beat Regularity Analysis**: Measure how regular/consistent the beats are
- **Multiple Algorithm Support**: Uses both librosa and madmom for improved accuracy

## Requirements

```
librosa>=0.11.0
madmom>=0.16.1
numpy>=1.20.0
```

## Usage

### Basic Usage

```python
from app.utils.audio import get_beat_timestamps

# Get a list of beat timestamps in seconds
beat_times = get_beat_timestamps("path/to/audio.mp3")
print(f"Found {len(beat_times)} beats")
print(f"First few beats: {beat_times[:5]}")
```

### Advanced Usage

```python
from app.utils.audio import analyze_beats

# Get comprehensive beat analysis
analysis = analyze_beats("path/to/audio.mp3")

# Access various properties
print(f"Tempo: {analysis['tempo_bpm']} BPM")
print(f"Total beats: {analysis['total_beats']}")
print(f"Beat regularity: {analysis['beat_regularity']}")  # Lower is more regular
print(f"Downbeats: {analysis['downbeat_timestamps']}")
```

## API Endpoints

The module also exposes FastAPI endpoints for beat detection:

### 1. Basic Beat Detection

```http
POST /audio/beats
```

Upload an audio file and receive timestamps of all detected beats.

### 2. Comprehensive Analysis

```http
POST /audio/analyze
```

Upload an audio file and receive comprehensive beat analysis including tempo, regularity, and downbeats.

## Implementation Details

The module uses a hybrid approach for beat detection:

1. **Primary Method**: Uses madmom's DBN beat tracker with recurrent neural networks
2. **Fallback Method**: Uses librosa's dynamic programming beat tracker if madmom fails

This hybrid approach ensures robust beat detection across various types of audio files.

## Testing

You can test the module using the included test script:

```bash
python -m app.utils.audio.test_beat_detector path/to/audio.mp3
```

This will run both basic and comprehensive beat analysis on the provided audio file and display the results.

## Examples

See `test_beat_detector.py` for more detailed examples of usage. 
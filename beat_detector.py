import librosa
import numpy as np
import matplotlib.pyplot as plt

# Load an audio file from librosa's example collection
print("Loading audio file...")
y, sr = librosa.load(librosa.ex('choice'), duration=10)
print(f"Audio loaded: sample rate={sr}Hz, duration={len(y)/sr:.2f}s")

# Method 1: Beat tracking (returns tempo and beat frames)
print("\nPerforming beat tracking...")
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
print(f"Estimated tempo: {tempo.item():.2f} BPM")
print(f"Beat frames: {beats[:10]}... (showing first 10)")

# Convert beat frames to timestamps
beat_times = librosa.frames_to_time(beats, sr=sr)
print(f"Beat times: {beat_times[:10]}... (showing first 10 in seconds)")

# Method 2: Use tempo function directly
print("\nEstimating tempo directly...")
onset_env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)
tempo_direct = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
print(f"Directly estimated tempo: {tempo_direct.item():.2f} BPM")

# Visualize the beats over the onset strength envelope
print("\nCreating visualization...")
plt.figure(figsize=(12, 6))
times = librosa.times_like(onset_env, sr=sr)
plt.plot(times, librosa.util.normalize(onset_env), label='Onset strength')
plt.vlines(beat_times, 0, 1, alpha=0.5, color='r', linestyle='--', label='Beats')
plt.title(f'Onset Strength Envelope and Detected Beats (Tempo: {tempo.item():.1f} BPM)')
plt.xlabel('Time (s)')
plt.ylabel('Normalized strength')
plt.legend()
plt.tight_layout()
plt.savefig('beat_detection_result.png')
print("Visualization saved as 'beat_detection_result.png'")

print("\nBeat detection completed successfully!") 
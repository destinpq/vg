# Fixed Setup for Video Generator Backend

This guide explains how to run the backend with the fixes applied to address the dependency issues and port conflicts.

## Overview of Fixes

1. **Mochi Integration Issue**: 
   - Fixed the Mochi integration by creating a simplified demo implementation
   - Avoided the installation errors by not directly depending on the Mochi package

2. **Port Conflict Issue**:
   - Changed the backend port from 8000 to 50080 (to avoid permission issues)
   - Updated frontend configuration to use the new port

## Setup Instructions

### Step 1: Activate the Virtual Environment

```powershell
# Navigate to the backend directory
cd backend

# Activate the virtual environment
.\venv\Scripts\activate
```

### Step 2: Install Dependencies

Run the modified installation script:

```powershell
python install_mochi_deps.py
```

This will:
- Copy the Mochi demo scripts to a local directory
- Install minimal dependencies needed for video generation

### Step 3: Configure FFmpeg

Make sure FFmpeg is in your PATH:

```powershell
# Get the absolute path to the ffmpeg directory
$ffmpegPath = Resolve-Path -Path "..\ffmpeg"

# Add it to the PATH for the current session
$env:PATH = "$env:PATH;$ffmpegPath"
```

### Step 4: Start the Backend Server

Start the server on port 50080:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 50080 --reload
```

Or use the provided script:

```powershell
.\setup_and_run.ps1
```

### Step 5: Update Frontend Configuration

Make sure the frontend is configured to use port 50080:

1. Create or update the `.env` file in the frontend directory:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:50080
   ```

2. Restart the frontend development server.

## Troubleshooting

### Port Still in Use

If port 50080 is also in use, you can try another port:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 60080 --reload
```

Just remember to update the frontend configuration to match.

### Permission Issues

If you're still encountering permission errors, try:

1. Running PowerShell as Administrator
2. Disabling any security software temporarily
3. Using a non-privileged port (ports above 49152 are typically less restricted)

### FFmpeg Not Found

If you see "FFmpeg not found - using OpenCV native MP4 encoding", make sure:

1. FFmpeg executables are properly extracted in the ffmpeg directory
2. The FFmpeg directory is correctly added to the PATH

### Video Generation Issues

If you encounter issues with video generation:

1. Check the backend logs for specific error messages
2. Verify that the simplified demo script is working correctly
3. Try using a simpler prompt

## API Endpoints

The API should now be available at:

- API Base URL: http://localhost:50080
- API Documentation: http://localhost:50080/docs
- Video Generation: http://localhost:50080/video/generate
- Video Status: http://localhost:50080/video/status/{video_id}

## Reverting to Original Implementation

If you want to try the original implementation with the full Mochi model:

1. Fix the issues in the Mochi package's setup script
2. Modify the `install_mochi_deps.py` to properly install dependencies
3. Update the `ai_core.py` to use the actual Mochi CLI 
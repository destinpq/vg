#!/bin/bash

# Make script exit on error
set -e

# Change to the ai_engine directory
cd "$(dirname "$0")/ai_engine"
echo "Changed to $(pwd) directory"

# Load environment variables from .env if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Check if results directory exists, create if not
if [ ! -d "${RESULTS_DIR:-./results}" ]; then
    echo "Creating results directory at ${RESULTS_DIR:-./results}"
    mkdir -p "${RESULTS_DIR:-./results}"
fi

# Bypass NVML version check
export __NVML_RUNTIME_DISABLED=1
echo "Bypassing NVIDIA driver/library version check..."

# Ensure we have the proper Python packages
echo "Installing/updating required packages..."
python3 -m pip install -r requirements_h100.txt

# Default settings
USE_NGROK=true
PORT=8000
MAX_CONCURRENT_JOBS=${MAX_CONCURRENT_JOBS:-4}
DEBUG=""

# Parse command-line arguments
for arg in "$@"; do
    case $arg in
        --no-ngrok)
            USE_NGROK=false
            shift
            ;;
        --port=*)
            PORT="${arg#*=}"
            shift
            ;;
        --max-concurrent-jobs=*)
            MAX_CONCURRENT_JOBS="${arg#*=}"
            shift
            ;;
        --debug)
            DEBUG="--debug"
            shift
            ;;
    esac
done

# Export for child processes
export MAX_CONCURRENT_JOBS

# Start the service
if [ "$USE_NGROK" = true ]; then
    echo "Starting HunyuanVideo service with ngrok on port $PORT..."
    echo "Maximum concurrent jobs: $MAX_CONCURRENT_JOBS"
    python3 setup_ngrok.py --port $PORT --max-concurrent-jobs $MAX_CONCURRENT_JOBS $DEBUG
else
    echo "Starting HunyuanVideo service (without ngrok) on port $PORT..."
    echo "Maximum concurrent jobs: $MAX_CONCURRENT_JOBS"
    python3 hunyuan_video_app.py --port $PORT --max-concurrent-jobs $MAX_CONCURRENT_JOBS $DEBUG
fi 
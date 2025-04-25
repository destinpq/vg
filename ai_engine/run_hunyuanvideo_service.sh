#!/bin/bash

# Make script exit on error
set -e

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

# Print GPU information
echo "Checking GPU information..."
nvidia-smi

# Ensure we have the proper Python packages
echo "Installing/updating required packages..."
pip install -r requirements_h100.txt

# Default settings
USE_NGROK=true
PORT=8080
MAX_CONCURRENT_JOBS=${MAX_CONCURRENT_JOBS:-1}
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
    python setup_ngrok.py --port $PORT --max-concurrent-jobs $MAX_CONCURRENT_JOBS $DEBUG
else
    echo "Starting HunyuanVideo service (without ngrok) on port $PORT..."
    echo "Maximum concurrent jobs: $MAX_CONCURRENT_JOBS"
    python hunyuan_video_app.py --port $PORT --max-concurrent-jobs $MAX_CONCURRENT_JOBS $DEBUG
fi 
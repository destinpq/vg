#!/usr/bin/env python3
"""
Script to download Hunyuan Video model weights from HuggingFace.
This script handles:
1. Authentication with HuggingFace (if token is provided)
2. Downloading the model weights
3. Verifying the downloaded files
"""
import os
import sys
import time
import argparse
import logging
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download, HfApi

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
MODEL_ID = "tencent/HunyuanVideo"
CHECKPOINTS_DIR = "/root/output/hunyuan-models"
REQUIRED_FILES = [
    "config.json",
    "model_index.json",
    "scheduler_config.json"
]

def setup_hf_auth(token):
    """Set up HuggingFace authentication"""
    if token:
        logger.info("Setting up HuggingFace authentication")
        os.environ["HUGGING_FACE_HUB_TOKEN"] = token
        api = HfApi(token=token)
        # Test authentication
        try:
            api.whoami()
            logger.info("Successfully authenticated with HuggingFace")
            return True
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    else:
        logger.info("No token provided, proceeding without authentication")
        return True

def download_weights(token=None):
    """Download the model weights from HuggingFace"""
    logger.info(f"Starting download of model weights for {MODEL_ID}")
    logger.info(f"Weights will be saved to {CHECKPOINTS_DIR}")
    
    # Ensure the checkpoints directory exists
    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
    
    # Set up authentication if token is provided
    if token and not setup_hf_auth(token):
        logger.error("Failed to authenticate with HuggingFace. Aborting download.")
        return False
    
    try:
        # Estimate size before downloading
        logger.info("Estimating download size (this may take a moment)...")
        try:
            # Try to estimate size (not always possible)
            api = HfApi(token=token if token else None)
            repo_info = api.repo_info(MODEL_ID)
            logger.info(f"Repository size: {repo_info.size_on_disk / (1024**3):.2f} GB")
        except Exception as e:
            logger.warning(f"Could not estimate repository size: {str(e)}")

        # Start download with progress
        logger.info(f"Downloading {MODEL_ID} to {CHECKPOINTS_DIR}...")
        start_time = time.time()
        
        # Use snapshot_download for the entire repository
        snapshot_download(
            repo_id=MODEL_ID,
            local_dir=CHECKPOINTS_DIR,
            local_dir_use_symlinks=False,
            token=token,
            resume_download=True,
            ignore_patterns=["*.md", "*.txt"]
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Download completed in {elapsed_time:.2f} seconds")
        
        # Verify downloaded files
        return verify_download()
        
    except Exception as e:
        logger.error(f"Error downloading weights: {str(e)}")
        return False

def verify_download():
    """Verify that all required files were downloaded"""
    logger.info("Verifying downloaded files...")
    
    # Check for required files
    missing_files = []
    for file in REQUIRED_FILES:
        file_path = os.path.join(CHECKPOINTS_DIR, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    # Count model files
    model_files = list(Path(CHECKPOINTS_DIR).glob("**/*.safetensors"))
    bin_files = list(Path(CHECKPOINTS_DIR).glob("**/*.bin"))
    
    logger.info(f"Found {len(model_files)} .safetensors files and {len(bin_files)} .bin files")
    
    total_size = sum(f.stat().st_size for f in model_files + bin_files) / (1024**3)
    logger.info(f"Total model size: {total_size:.2f} GB")
    
    # Assume success if we found any model files
    return len(model_files) > 0 or len(bin_files) > 0

def main():
    parser = argparse.ArgumentParser(description="Download Hunyuan Video model weights")
    parser.add_argument("--token", type=str, help="HuggingFace token for authentication")
    parser.add_argument("--model-id", type=str, default=MODEL_ID, help="HuggingFace model ID")
    parser.add_argument("--output-dir", type=str, default=CHECKPOINTS_DIR, help="Directory to save model weights")
    args = parser.parse_args()
    
    # Update globals if custom values provided
    global MODEL_ID, CHECKPOINTS_DIR
    MODEL_ID = args.model_id
    CHECKPOINTS_DIR = args.output_dir
    
    logger.info("Starting Hunyuan Video model weights download")
    logger.info(f"Model ID: {MODEL_ID}")
    logger.info(f"Output directory: {CHECKPOINTS_DIR}")
    
    success = download_weights(args.token)
    
    if success:
        logger.info("Model weights downloaded and verified successfully!")
        return 0
    else:
        logger.error("Failed to download or verify model weights.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
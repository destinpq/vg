#!/usr/bin/env python3
"""
Run script for the HunyuanVideo generator service.
"""

import os
import argparse
import logging
from ai_engine import run_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HunyuanVideoRunner")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run HunyuanVideo Generator Service")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run on")
    parser.add_argument("--port", type=int, default=8080, help="Port to run on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--max-concurrent-jobs", type=int, help="Maximum concurrent jobs")
    
    args = parser.parse_args()
    
    # Print GPU information
    try:
        import torch
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            logger.info(f"Found {device_count} CUDA device(s)")
            
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                device_mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                logger.info(f"GPU {i}: {device_name} with {device_mem:.1f} GB memory")
                
                # Check for H100
                if "H100" in device_name:
                    logger.info(f"Detected H100 GPU - optimal performance expected")
        else:
            logger.warning("No CUDA devices found - video generation will be very slow!")
    except:
        logger.warning("Failed to get GPU information")
    
    # Run the app
    run_app(
        host=args.host,
        port=args.port,
        debug=args.debug,
        max_concurrent_jobs=args.max_concurrent_jobs
    ) 
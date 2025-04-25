#!/usr/bin/env python3
"""
Run the HunyuanVideo generator service with ngrok for public access.
"""

import os
import sys
import subprocess
import argparse
import time
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HunyuanVideoNgrok")

# Load environment variables
load_dotenv()

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        subprocess.run(["./ngrok", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ngrok():
    """Download and install ngrok"""
    logger.info("Installing ngrok...")
    
    # Download ngrok
    subprocess.run([
        "wget", "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip",
        "-O", "ngrok.zip"
    ], check=True)
    
    # Unzip ngrok
    subprocess.run(["unzip", "-o", "ngrok.zip"], check=True)
    
    # Make ngrok executable
    subprocess.run(["chmod", "+x", "ngrok"], check=True)
    
    # Clean up
    os.remove("ngrok.zip")
    
    logger.info("ngrok installed successfully")

def setup_ngrok_auth(auth_token=None):
    """Set up ngrok authentication"""
    if not auth_token:
        auth_token = os.getenv("NGROK_AUTH_TOKEN")
    
    if not auth_token:
        logger.warning("No ngrok auth token provided. Running with limited features.")
        return False
    
    logger.info("Setting up ngrok authentication...")
    subprocess.run(["./ngrok", "authtoken", auth_token], check=True)
    logger.info("ngrok authentication set up successfully")
    return True

def start_ngrok(port=8080):
    """Start ngrok HTTP tunnel to the specified port"""
    logger.info(f"Starting ngrok tunnel to port {port}...")
    
    # Start ngrok in the background
    process = subprocess.Popen(
        ["./ngrok", "http", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for ngrok to start up
    time.sleep(3)
    
    # Get the public URL from the ngrok API
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()["tunnels"]
        
        if not tunnels:
            logger.error("No tunnels found. ngrok may have failed to start properly.")
            return None
        
        # Get the HTTPS tunnel URL
        https_tunnel = next((t for t in tunnels if t["proto"] == "https"), tunnels[0])
        public_url = https_tunnel["public_url"]
        
        logger.info(f"ngrok tunnel started: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Failed to get ngrok public URL: {e}")
        return None

def run_flask_app(host="0.0.0.0", port=8080, debug=False, max_concurrent_jobs=None):
    """Run the HunyuanVideo Flask app"""
    cmd = [
        "python", "run.py",
        "--host", host,
        "--port", str(port)
    ]
    
    if debug:
        cmd.append("--debug")
    
    if max_concurrent_jobs is not None:
        cmd.extend(["--max-concurrent-jobs", str(max_concurrent_jobs)])
    
    # Run the Flask app as a subprocess
    # We don't use the imported run_app function directly because we want this process
    # to be a separate process that we can terminate when needed
    logger.info(f"Starting Flask app: {' '.join(cmd)}")
    process = subprocess.Popen(cmd)
    
    return process

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run HunyuanVideo Generator with ngrok")
    parser.add_argument("--port", type=int, default=8080, help="Port to tunnel to")
    parser.add_argument("--auth-token", type=str, help="ngrok auth token")
    parser.add_argument("--debug", action="store_true", help="Run Flask in debug mode")
    parser.add_argument("--max-concurrent-jobs", type=int, help="Maximum concurrent jobs")
    
    args = parser.parse_args()
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        logger.info("ngrok not found, installing...")
        install_ngrok()
    else:
        logger.info("ngrok is already installed")
    
    # Set up ngrok authentication
    setup_ngrok_auth(args.auth_token)
    
    # Start ngrok tunnel
    public_url = start_ngrok(args.port)
    
    if public_url:
        logger.info("-" * 80)
        logger.info("HunyuanVideo is now accessible at the following URL:")
        logger.info(f"{public_url}")
        logger.info("Share this URL with anyone who needs to access your HunyuanVideo generator")
        logger.info("-" * 80)
        
        # Run the Flask app in the foreground
        flask_process = run_flask_app(
            port=args.port, 
            debug=args.debug, 
            max_concurrent_jobs=args.max_concurrent_jobs
        )
        
        try:
            # Wait for the Flask app to exit
            flask_process.wait()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt detected, shutting down...")
            flask_process.terminate()
            sys.exit(0)
    else:
        logger.error("Failed to start ngrok tunnel. Exiting.")
        sys.exit(1) 
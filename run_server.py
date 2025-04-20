#!/usr/bin/env python
"""
Server launcher for AI Video Generator
This script runs the correct server file and ensures proper directory configuration
"""
import os
import sys
import subprocess
from pathlib import Path

def ensure_output_directories():
    """Make sure both output directories exist and are in sync"""
    # Create both output directories if they don't exist
    output_dir = Path("output")
    outputs_dir = Path("outputs")
    
    output_dir.mkdir(exist_ok=True)
    outputs_dir.mkdir(exist_ok=True)
    
    # Print which directories we're using
    print(f"✅ Using output directory: {output_dir.absolute()}")
    print(f"✅ Using outputs directory: {outputs_dir.absolute()}")
    
    # Copy contents from outputs to output to ensure everything is available
    try:
        # For Windows, use robocopy
        if os.name == 'nt':
            # Only run if there are files to copy
            if any(outputs_dir.iterdir()):
                os.system(f'robocopy "{outputs_dir}" "{output_dir}" /E /NFL /NDL /NJH /NJS /nc /ns /np > nul 2>&1')
                print("✅ Synchronized files from outputs/ to output/")
        # For Unix-like systems (Linux, macOS)
        else:
            os.system(f'rsync -a "{outputs_dir}/" "{output_dir}/" > /dev/null 2>&1')
            print("✅ Synchronized files from outputs/ to output/")
    except Exception as e:
        print(f"⚠️ Warning: Could not synchronize directories: {e}")

def run_server():
    """Run the correct main.py file"""
    # Always use the root main.py as our primary entry point
    main_path = Path("main.py")
    
    if not main_path.exists():
        print("❌ Error: main.py not found in the current directory")
        return 1
    
    print(f"🚀 Starting server using: {main_path.absolute()}")
    
    # Run the server
    cmd = [sys.executable, str(main_path)]
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
        return 0

if __name__ == "__main__":
    # Setup output directories first
    ensure_output_directories()
    
    # Then run the server
    sys.exit(run_server()) 
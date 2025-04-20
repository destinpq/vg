"""
Main entry point for the AI Video Generator API.
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath("."))

# Create output directories
output_dir = Path("output")
outputs_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)
outputs_dir.mkdir(exist_ok=True)

print("Starting server...")
print(f"Output directory: {output_dir.absolute()}")
print(f"Outputs directory: {outputs_dir.absolute()}")

# Handle both output and outputs directories
if outputs_dir.exists() and any(outputs_dir.iterdir()):
    print("Synchronizing directories...")
    if os.name == "nt":
        os.system('robocopy "outputs" "output" /E /NFL /NDL /NJH /NJS /nc /ns /np > nul 2>&1')
    else:
        os.system('rsync -a "outputs/" "output/" > /dev/null 2>&1')

print("Server ready.")

# Launch the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=5001, reload=True)

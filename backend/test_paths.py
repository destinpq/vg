import os
from pathlib import Path
from app.utils.config import get_settings

# Get settings
settings = get_settings()

# Print key directories
print("=" * 50)
print("OUTPUT PATH CONFIGURATION")
print("=" * 50)
print(f"Current directory: {os.getcwd()}")
print(f"OUTPUT_DIR: {settings.OUTPUT_DIR} (exists: {os.path.exists(settings.OUTPUT_DIR)})")
print(f"VIDEO_OUTPUT_DIR: {settings.VIDEO_OUTPUT_DIR} (exists: {os.path.exists(settings.VIDEO_OUTPUT_DIR)})")
print(f"OUTPUTS_DIR: {settings.OUTPUTS_DIR} (exists: {os.path.exists(settings.OUTPUTS_DIR)})")
print("=" * 50)

# Create test file
test_dir = os.path.join(settings.OUTPUT_DIR, "test_dir")
os.makedirs(test_dir, exist_ok=True)
test_file = os.path.join(test_dir, "test_file.txt")

with open(test_file, "w") as f:
    f.write("This is a test file to verify static file serving")

print(f"Created test file at: {test_file}")
print(f"Test URL would be: {settings.VIDEO_BASE_URL}/output/test_dir/test_file.txt")
print("=" * 50) 
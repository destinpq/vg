"""
File utilities for handling files and directories.
"""
import os
import shutil
from pathlib import Path
import tempfile
import logging

logger = logging.getLogger(__name__)

def ensure_directory(directory_path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory (string or Path object)
        
    Returns:
        Path object for the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def safe_delete(file_path):
    """
    Safely delete a file if it exists.
    
    Args:
        file_path: Path to the file (string or Path object)
        
    Returns:
        True if the file was deleted, False otherwise
    """
    path = Path(file_path)
    if path.exists():
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            return True
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
            return False
    return False

def create_temp_directory():
    """
    Create a temporary directory.
    
    Returns:
        Path object for the temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    return Path(temp_dir)

def create_temp_file(suffix=None):
    """
    Create a temporary file.
    
    Args:
        suffix: Optional file suffix (e.g., '.mp4')
        
    Returns:
        Path object for the temporary file
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return Path(path)

def get_file_size(file_path):
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file (string or Path object)
        
    Returns:
        Size of the file in bytes, or 0 if the file doesn't exist
    """
    path = Path(file_path)
    if path.exists() and path.is_file():
        return path.stat().st_size
    return 0

def get_file_extension(file_path):
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file (string or Path object)
        
    Returns:
        Extension of the file (e.g., 'mp4') without the dot
    """
    return Path(file_path).suffix.lstrip('.')

def is_video_file(file_path):
    """
    Check if a file is a video file based on its extension.
    
    Args:
        file_path: Path to the file (string or Path object)
        
    Returns:
        True if the file is a video file, False otherwise
    """
    video_extensions = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv']
    return get_file_extension(file_path).lower() in video_extensions

def is_image_file(file_path):
    """
    Check if a file is an image file based on its extension.
    
    Args:
        file_path: Path to the file (string or Path object)
        
    Returns:
        True if the file is an image file, False otherwise
    """
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    return get_file_extension(file_path).lower() in image_extensions

def copy_file(source, destination):
    """
    Copy a file from source to destination.
    
    Args:
        source: Path to the source file (string or Path object)
        destination: Path to the destination file (string or Path object)
        
    Returns:
        Path object for the destination file
    """
    src_path = Path(source)
    dst_path = Path(destination)
    
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")
    
    # Ensure the destination directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy the file
    shutil.copy2(src_path, dst_path)
    return dst_path 
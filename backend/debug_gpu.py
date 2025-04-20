"""
GPU Debugging Script for Hunyuan

This script performs various tests to verify GPU availability, memory, and
compatibility with the Hunyuan video generation model.
"""

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gpu_debug.log')
    ]
)

logger = logging.getLogger("gpu_debug")

def check_system_info():
    """Check basic system information"""
    logger.info("=" * 50)
    logger.info("SYSTEM INFORMATION")
    logger.info("=" * 50)
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info("-" * 50)

def check_torch_installation():
    """Check PyTorch installation and CUDA compatibility"""
    logger.info("=" * 50)
    logger.info("PYTORCH AND CUDA CHECK")
    logger.info("=" * 50)
    
    try:
        import torch
        logger.info(f"PyTorch version: {torch.__version__}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"Number of GPUs: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                logger.info(f"GPU {i}: {torch.cuda.get_device_name(i)}")
                logger.info(f"GPU {i} memory: {torch.cuda.get_device_properties(i).total_memory / (1024**3):.2f} GB")
            
            # Test CUDA functionality
            logger.info("Testing CUDA tensor operations...")
            x = torch.randn(10, 10).cuda()
            y = torch.randn(10, 10).cuda()
            z = x @ y
            logger.info(f"CUDA tensor operation successful: {z.size()}")
            
            # Try a more complex operation
            logger.info("Testing CUDA convolution...")
            try:
                conv = torch.nn.Conv2d(3, 16, 3).cuda()
                input_tensor = torch.randn(1, 3, 32, 32).cuda()
                output = conv(input_tensor)
                logger.info(f"CUDA convolution successful: {output.size()}")
            except Exception as e:
                logger.error(f"CUDA convolution failed: {e}")
                
        else:
            logger.warning("CUDA is not available.")
            logger.info("Checking if NVIDIA drivers are installed...")
            
            # Check NVIDIA drivers on different platforms
            if platform.system() == "Windows":
                try:
                    output = subprocess.check_output("nvidia-smi", shell=True).decode()
                    logger.info("NVIDIA drivers are installed:")
                    logger.info(output[:500] + "..." if len(output) > 500 else output)
                except subprocess.CalledProcessError:
                    logger.error("NVIDIA drivers not found or not working properly.")
                    logger.info("Please install NVIDIA drivers from: https://www.nvidia.com/Download/index.aspx")
            elif platform.system() == "Linux":
                try:
                    output = subprocess.check_output("nvidia-smi", shell=True).decode()
                    logger.info("NVIDIA drivers are installed:")
                    logger.info(output[:500] + "..." if len(output) > 500 else output)
                except subprocess.CalledProcessError:
                    logger.error("NVIDIA drivers not found or not working properly.")
            
            logger.info("CUDA installation suggestions:")
            logger.info("1. Install NVIDIA drivers")
            logger.info("2. Install CUDA Toolkit from: https://developer.nvidia.com/cuda-downloads")
            logger.info("3. Reinstall PyTorch with CUDA support: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    
    except ImportError:
        logger.error("PyTorch is not installed.")
        logger.info("Install PyTorch with: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    
    logger.info("-" * 50)

def check_hunyuan_requirements():
    """Check requirements specifically for Hunyuan"""
    logger.info("=" * 50)
    logger.info("HUNYUAN-SPECIFIC REQUIREMENTS")
    logger.info("=" * 50)
    
    requirements = {
        "torch": "2.4.0 or newer",
        "numpy": "Any recent version",
        "xformers": "0.0.23 or newer",
        "flash-attention": "2.6.3 or newer",
        "xfuser": "0.4.0",
        "transformers": "Any recent version",
        "git": "For cloning repository",
        "ffmpeg": "For video processing"
    }
    
    for package, version in requirements.items():
        try:
            if package == "torch":
                import torch
                logger.info(f"✓ {package}: {torch.__version__} (required: {version})")
            elif package == "numpy":
                import numpy
                logger.info(f"✓ {package}: {numpy.__version__} (required: {version})")
            elif package == "xformers":
                try:
                    import xformers
                    logger.info(f"✓ {package}: Installed (required: {version})")
                except ImportError:
                    logger.warning(f"✗ {package}: Not installed (required: {version})")
            elif package == "transformers":
                try:
                    import transformers
                    logger.info(f"✓ {package}: {transformers.__version__} (required: {version})")
                except ImportError:
                    logger.warning(f"✗ {package}: Not installed (required: {version})")
            elif package == "git":
                try:
                    output = subprocess.check_output("git --version", shell=True).decode().strip()
                    logger.info(f"✓ {package}: {output} (required: {version})")
                except subprocess.CalledProcessError:
                    logger.warning(f"✗ {package}: Not installed or not in PATH (required: {version})")
            elif package == "ffmpeg":
                try:
                    output = subprocess.check_output("ffmpeg -version", shell=True).decode().split('\n')[0]
                    logger.info(f"✓ {package}: {output} (required: {version})")
                except subprocess.CalledProcessError:
                    logger.warning(f"✗ {package}: Not installed or not in PATH (required: {version})")
            else:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "show", package], 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL)
                    logger.info(f"✓ {package}: Installed (required: {version})")
                except subprocess.CalledProcessError:
                    logger.warning(f"✗ {package}: Not installed (required: {version})")
        except Exception as e:
            logger.warning(f"✗ {package}: Error checking - {str(e)}")
    
    # Check for minimum GPU memory
    try:
        import torch
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            if gpu_memory >= 24:
                logger.info(f"✓ GPU Memory: {gpu_memory:.2f} GB (Excellent for Hunyuan)")
            elif gpu_memory >= 12:
                logger.info(f"✓ GPU Memory: {gpu_memory:.2f} GB (Good for Hunyuan with reduced settings)")
            elif gpu_memory >= 8:
                logger.warning(f"⚠ GPU Memory: {gpu_memory:.2f} GB (Minimum for Hunyuan with very low settings)")
            else:
                logger.error(f"✗ GPU Memory: {gpu_memory:.2f} GB (Insufficient for Hunyuan)")
    except:
        logger.warning("Could not check GPU memory")
    
    logger.info("-" * 50)

def check_model_paths():
    """Check if model paths exist and have correct permissions"""
    logger.info("=" * 50)
    logger.info("MODEL PATHS CHECK")
    logger.info("=" * 50)
    
    # Common model directories
    model_dirs = [
        "model_cache",
        "model_cache/hunyuan",
        "backend/model_cache",
        "backend/model_cache/hunyuan"
    ]
    
    for directory in model_dirs:
        if os.path.exists(directory):
            logger.info(f"Directory exists: {directory}")
            logger.info(f"  Readable: {os.access(directory, os.R_OK)}")
            logger.info(f"  Writable: {os.access(directory, os.W_OK)}")
            
            # Check space
            try:
                import shutil
                total, used, free = shutil.disk_usage(os.path.abspath(directory))
                logger.info(f"  Disk space - Total: {total/(1024**3):.2f} GB, Free: {free/(1024**3):.2f} GB")
                
                if free < 10 * (1024**3):  # Less than 10 GB
                    logger.warning(f"  Low disk space: {free/(1024**3):.2f} GB free. Hunyuan needs ~10 GB for models.")
            except Exception as e:
                logger.warning(f"  Could not check disk space: {e}")
                
            # List files if they exist
            files = os.listdir(directory)
            if files:
                logger.info(f"  Files ({len(files)}): {', '.join(files[:5])}{'...' if len(files) > 5 else ''}")
            else:
                logger.info(f"  Directory is empty")
        else:
            logger.info(f"Directory does not exist: {directory}")
    
    logger.info("-" * 50)

def fix_common_issues():
    """Attempt to fix common issues"""
    logger.info("=" * 50)
    logger.info("ATTEMPTING TO FIX COMMON ISSUES")
    logger.info("=" * 50)
    
    # Create model directories
    model_dirs = ["model_cache", "model_cache/hunyuan"]
    for directory in model_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
    
    # Install common dependencies
    dependencies = [
        "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
        "numpy",
        "requests",
        "tqdm"
    ]
    
    for dep in dependencies:
        try:
            logger.info(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U"] + dep.split())
            logger.info(f"Successfully installed {dep}")
        except Exception as e:
            logger.error(f"Failed to install {dep}: {e}")
    
    logger.info("-" * 50)

def main():
    """Main function to run all checks"""
    logger.info("Starting GPU and Hunyuan compatibility check...")
    
    check_system_info()
    check_torch_installation() 
    check_hunyuan_requirements()
    check_model_paths()
    
    logger.info("=" * 50)
    logger.info("SUMMARY AND RECOMMENDATIONS")
    logger.info("=" * 50)
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            logger.info(f"GPU Status: Available ({torch.cuda.get_device_name(0)})")
            
            if gpu_memory >= 24:
                logger.info("Hunyuan Compatibility: Excellent")
                logger.info("Recommended settings:")
                logger.info("- Resolution: 720p or higher (1280x720)")
                logger.info("- Video length: Up to 5-10 seconds (150-300 frames)")
            elif gpu_memory >= 16:
                logger.info("Hunyuan Compatibility: Good")
                logger.info("Recommended settings:")
                logger.info("- Resolution: 720p (1280x720)")
                logger.info("- Video length: 3-5 seconds (90-150 frames)")
            elif gpu_memory >= 12:
                logger.info("Hunyuan Compatibility: Moderate")
                logger.info("Recommended settings:")
                logger.info("- Resolution: 540p (960x540)")
                logger.info("- Video length: 2-3 seconds (60-90 frames)")
            elif gpu_memory >= 8:
                logger.info("Hunyuan Compatibility: Limited")
                logger.info("Recommended settings:")
                logger.info("- Resolution: 360p (640x360)")
                logger.info("- Video length: 1-2 seconds (30-60 frames)")
                logger.info("- Consider using FP8 or FP16 mode")
            else:
                logger.warning("Hunyuan Compatibility: Poor")
                logger.warning("Your GPU does not have enough memory for Hunyuan.")
                logger.warning("Consider using a cloud GPU service or upgrading your hardware.")
        else:
            logger.warning("GPU Status: Not Available")
            logger.warning("Hunyuan requires a CUDA-compatible GPU to run effectively.")
    except:
        logger.warning("Could not determine GPU compatibility")
    
    logger.info("=" * 50)
    logger.info("Would you like to attempt to fix common issues? (y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        fix_common_issues()
    
    logger.info("Check complete! See gpu_debug.log for detailed information.")

if __name__ == "__main__":
    main() 
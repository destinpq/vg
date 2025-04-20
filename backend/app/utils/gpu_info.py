"""
Utilities for getting GPU information and acceleration capabilities.
"""
import os
import sys
import subprocess
import platform
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

def get_gpu_info() -> Dict[str, Any]:
    """
    Get GPU information for the system.
    
    Returns:
        Dict with GPU information including vendor, model, and memory
    """
    gpu_info = {
        "gpu_available": False,
        "vendor": "Unknown",
        "model": "None",
        "memory_total": 0,
        "driver_version": "Unknown",
        "cuda_version": "Unknown",
    }
    
    try:
        # Check if torch is available
        import torch
        
        if torch.cuda.is_available():
            gpu_info["gpu_available"] = True
            gpu_info["device_count"] = torch.cuda.device_count()
            
            device_properties = torch.cuda.get_device_properties(0)
            gpu_info["model"] = device_properties.name
            gpu_info["memory_total"] = round(device_properties.total_memory / (1024**3), 2)  # in GB
            
            # Try to determine vendor
            if "nvidia" in device_properties.name.lower():
                gpu_info["vendor"] = "NVIDIA"
            elif "amd" in device_properties.name.lower():
                gpu_info["vendor"] = "AMD"
            elif "intel" in device_properties.name.lower():
                gpu_info["vendor"] = "Intel"
                
            # Get CUDA version
            if hasattr(torch.version, 'cuda'):
                gpu_info["cuda_version"] = torch.version.cuda
                
            logger.info(f"GPU detected: {gpu_info['model']} with {gpu_info['memory_total']} GB")
        else:
            logger.warning("No CUDA-capable GPU detected")
    
    except ImportError:
        logger.warning("PyTorch not available, can't get GPU information")
    except Exception as e:
        logger.error(f"Error getting GPU information: {str(e)}")
    
    return gpu_info

def get_gpu_acceleration_info() -> Dict[str, bool]:
    """
    Get information about GPU acceleration capabilities.
    
    Returns:
        Dict with information about GPU acceleration capabilities
    """
    acceleration_info = {
        "cuda_available": False,
        "cudnn_available": False,
        "mps_available": False,  # Apple Metal Performance Shaders
        "directml_available": False,  # DirectML for Windows
        "rocm_available": False,  # ROCm for AMD GPUs
    }
    
    try:
        import torch
        
        # Check CUDA
        acceleration_info["cuda_available"] = torch.cuda.is_available()
        
        # Check cuDNN
        if acceleration_info["cuda_available"]:
            try:
                # This is a way to check for cuDNN
                if torch.backends.cudnn.is_available():
                    acceleration_info["cudnn_available"] = True
            except:
                pass
        
        # Check MPS (Metal Performance Shaders for Apple Silicon)
        if hasattr(torch.backends, "mps"):
            acceleration_info["mps_available"] = torch.backends.mps.is_available()
        
        # Check for DirectML (Windows)
        if platform.system() == "Windows":
            try:
                import torch_directml
                acceleration_info["directml_available"] = True
            except ImportError:
                pass
        
        # Check for ROCm (AMD)
        if acceleration_info["cuda_available"]:
            if "hip" in torch.__version__.lower() or "rocm" in torch.__version__.lower():
                acceleration_info["rocm_available"] = True
    
    except ImportError:
        logger.warning("PyTorch not available, can't get acceleration information")
    except Exception as e:
        logger.error(f"Error getting acceleration information: {str(e)}")
    
    return acceleration_info

def get_recommended_device() -> str:
    """
    Get the recommended device for machine learning based on available hardware.
    
    Returns:
        String indicating the recommended device ('cuda', 'mps', 'directml', or 'cpu')
    """
    try:
        import torch
        
        if torch.cuda.is_available():
            return "cuda"
        
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        
        if platform.system() == "Windows":
            try:
                import torch_directml
                return "directml"
            except ImportError:
                pass
        
        return "cpu"
    
    except ImportError:
        return "cpu"
    except Exception as e:
        logger.error(f"Error determining recommended device: {str(e)}")
        return "cpu"

def get_nvidia_smi_info() -> Dict[str, Any]:
    """
    Get detailed GPU information using nvidia-smi (NVIDIA only).
    
    Returns:
        Dict with detailed GPU information
    """
    info = {
        "available": False,
        "gpus": [],
        "driver_version": "Unknown",
        "cuda_version": "Unknown",
    }
    
    if platform.system() == "Windows":
        nvidia_smi = "nvidia-smi"
    else:
        nvidia_smi = "nvidia-smi"
    
    try:
        output = subprocess.check_output([nvidia_smi, "--query-gpu=name,memory.total,memory.free,memory.used,temperature.gpu,utilization.gpu", "--format=csv,noheader,nounits"])
        info["available"] = True
        
        lines = output.decode('utf-8').strip().split('\n')
        for line in lines:
            parts = [part.strip() for part in line.split(',')]
            if len(parts) >= 6:
                gpu_info = {
                    "name": parts[0],
                    "memory_total": float(parts[1]),
                    "memory_free": float(parts[2]),
                    "memory_used": float(parts[3]),
                    "temperature": float(parts[4]),
                    "utilization": float(parts[5]),
                }
                info["gpus"].append(gpu_info)
        
        # Get driver and CUDA version
        version_output = subprocess.check_output([nvidia_smi, "--query-gpu=driver_version,cuda_version", "--format=csv,noheader,nounits"])
        version_line = version_output.decode('utf-8').strip().split('\n')[0]
        version_parts = [part.strip() for part in version_line.split(',')]
        if len(version_parts) >= 2:
            info["driver_version"] = version_parts[0]
            info["cuda_version"] = version_parts[1]
    
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("nvidia-smi not available or failed")
    except Exception as e:
        logger.error(f"Error getting nvidia-smi information: {str(e)}")
    
    return info

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Print GPU information
    print("GPU Information:")
    gpu_info = get_gpu_info()
    for key, value in gpu_info.items():
        print(f"  {key}: {value}")
    
    print("\nAcceleration Information:")
    acceleration_info = get_gpu_acceleration_info()
    for key, value in acceleration_info.items():
        print(f"  {key}: {value}")
    
    print(f"\nRecommended Device: {get_recommended_device()}")
    
    # If NVIDIA GPU is available, print detailed information
    if gpu_info.get("vendor") == "NVIDIA":
        print("\nDetailed NVIDIA GPU Information:")
        nvidia_info = get_nvidia_smi_info()
        if nvidia_info.get("available"):
            print(f"  Driver Version: {nvidia_info.get('driver_version')}")
            print(f"  CUDA Version: {nvidia_info.get('cuda_version')}")
            for i, gpu in enumerate(nvidia_info.get("gpus", [])):
                print(f"\n  GPU {i+1}:")
                for key, value in gpu.items():
                    print(f"    {key}: {value}") 
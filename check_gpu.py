#!/usr/bin/env python3
"""
GPU Check Script for Video Generation App
This script checks whether the system has a GPU available and provides detailed information
"""

import os
import sys
import subprocess
import platform

def check_nvidia_drivers():
    """Check if NVIDIA drivers are installed properly"""
    try:
        result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except FileNotFoundError:
        return False, "NVIDIA SMI not found. NVIDIA drivers may not be installed."

def check_cuda():
    """Check CUDA availability and version using Python"""
    try:
        import torch
        if torch.cuda.is_available():
            return True, {
                "cuda_available": True,
                "cuda_version": torch.version.cuda,
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
                "device_name": torch.cuda.get_device_name(0),
                "memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB",
                "memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB",
                "memory_total": f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
            }
        else:
            return False, "CUDA is not available through PyTorch"
    except ImportError:
        return False, "PyTorch not installed"
    except Exception as e:
        return False, f"Error checking CUDA: {str(e)}"

def check_h100_gpu():
    """Check specifically for H100 GPU"""
    cuda_available, cuda_info = check_cuda()
    if cuda_available and isinstance(cuda_info, dict):
        device_name = cuda_info.get("device_name", "")
        if "H100" in device_name:
            memory_total = cuda_info.get("memory_total", "")
            if "80" in memory_total:  # Check if it's the 80GB variant
                return True, f"H100 GPU with 80GB detected: {device_name}"
            else:
                return True, f"H100 GPU detected, but not confirmed to be 80GB: {device_name}"
        else:
            return False, f"GPU detected but it's not an H100: {device_name}"
    else:
        return False, "No CUDA-capable GPU detected"

def check_mps():
    """Check for Apple Metal Performance Shaders (MPS) support"""
    try:
        import torch
        if hasattr(torch.backends, 'mps') and hasattr(torch.backends.mps, 'is_available'):
            if torch.backends.mps.is_available():
                return True, "MPS is available"
        return False, "MPS is not available"
    except ImportError:
        return False, "PyTorch not installed, cannot check MPS"
    except Exception as e:
        return False, f"Error checking MPS: {str(e)}"

def create_test_tensor():
    """Create a test tensor on GPU and perform a simple operation to verify functionality"""
    try:
        import torch
        if torch.cuda.is_available():
            # Create tensors on GPU
            x = torch.rand(1000, 1000, device='cuda')
            y = torch.rand(1000, 1000, device='cuda')
            
            # Time the matrix multiplication
            import time
            start = time.time()
            z = torch.matmul(x, y)
            torch.cuda.synchronize()  # Wait for GPU operation to complete
            elapsed = time.time() - start
            
            # Test passed if the tensor has the right shape and type
            if z.shape == (1000, 1000) and z.device.type == 'cuda':
                return True, f"GPU computation test passed. Matrix multiplication took {elapsed:.4f} seconds."
            else:
                return False, "GPU computation produced unexpected results."
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            # For Apple Silicon
            x = torch.rand(1000, 1000, device='mps')
            y = torch.rand(1000, 1000, device='mps')
            
            import time
            start = time.time()
            z = torch.matmul(x, y)
            elapsed = time.time() - start
            
            if z.shape == (1000, 1000) and z.device.type == 'mps':
                return True, f"MPS computation test passed. Matrix multiplication took {elapsed:.4f} seconds."
            else:
                return False, "MPS computation produced unexpected results."
        else:
            return False, "No GPU available for testing."
    except Exception as e:
        return False, f"Error during GPU computation test: {str(e)}"

def main():
    """Main function to run all checks"""
    print("=" * 50)
    print("GPU CONFIGURATION CHECK FOR VIDEO GENERATION")
    print("=" * 50)
    print(f"System: {platform.system()} {platform.version()}")
    print(f"Python: {sys.version}")
    
    # Check NVIDIA drivers
    print("\n1. Checking NVIDIA drivers...")
    drivers_ok, driver_info = check_nvidia_drivers()
    if drivers_ok:
        print("✅ NVIDIA drivers are properly installed.")
        print("-" * 50)
        print(driver_info)
        print("-" * 50)
    else:
        print(f"❌ NVIDIA driver issue: {driver_info}")
    
    # Check CUDA
    print("\n2. Checking CUDA availability...")
    cuda_ok, cuda_info = check_cuda()
    if cuda_ok:
        print("✅ CUDA is available and configured.")
        for key, value in cuda_info.items():
            print(f"   {key}: {value}")
    else:
        print(f"❌ CUDA issue: {cuda_info}")
        
        # Check MPS for Mac
        mps_ok, mps_info = check_mps()
        if mps_ok:
            print("✅ Apple MPS is available (alternative to CUDA for Mac).")
        else:
            print(f"❌ Apple MPS issue: {mps_info}")
    
    # Check H100 specifically
    print("\n3. Checking for H100 GPU...")
    h100_ok, h100_info = check_h100_gpu()
    if h100_ok:
        print(f"✅ {h100_info}")
    else:
        print(f"❌ {h100_info}")
    
    # Test GPU computation
    print("\n4. Running GPU computation test...")
    test_ok, test_info = create_test_tensor()
    if test_ok:
        print(f"✅ {test_info}")
    else:
        print(f"❌ {test_info}")
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    if drivers_ok and cuda_ok and test_ok:
        print("✅ GPU is properly configured and working.")
        if h100_ok:
            print("✅ H100 GPU with 80GB VRAM is ready for video generation tasks!")
        else:
            print("⚠️ You don't have an H100 GPU, but your current GPU should work.")
    else:
        print("❌ There are issues with the GPU configuration.")
        print("   Please check the details above and ensure drivers are properly installed.")
    
    print("\nRecommended next steps:")
    if not drivers_ok:
        print("- Install NVIDIA drivers appropriate for your GPU")
    if not cuda_ok:
        print("- Install CUDA toolkit and ensure it's in your PATH")
    if drivers_ok and cuda_ok and not h100_ok:
        print("- Your GPU is working but isn't an H100. The application will still work but may be slower.")
    if all([drivers_ok, cuda_ok, h100_ok, test_ok]):
        print("- You're all set! Run 'docker-compose up -d' to start the video generation service")

if __name__ == "__main__":
    main() 
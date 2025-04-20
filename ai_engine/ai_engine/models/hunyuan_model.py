import os
import time
import torch
import logging
import subprocess
from pathlib import Path

class HunyuanModel:
    """
    Model class for interacting with the HunyuanVideo text-to-video generation model
    """
    def __init__(self, model_path=None, fp8_weights_path=None):
        """
        Initialize the HunyuanVideo model
        
        Args:
            model_path: Path to the model
            fp8_weights_path: Path to FP8 weights (for memory efficiency)
        """
        self.logger = logging.getLogger("HunyuanModel")
        self.model_path = model_path or os.getenv("HUNYUANVIDEO_MODEL_PATH", "/root/.cache/huggingface/hub")
        self.fp8_weights_path = fp8_weights_path or os.getenv("FP8_WEIGHTS_PATH")
        self.initialize_cuda()
        
    def initialize_cuda(self):
        """Apply CUDA optimizations specifically for H100 GPUs"""
        if not torch.cuda.is_available():
            self.logger.warning("CUDA not available. Using CPU (will be slow).")
            return
            
        # Set CUDA related environment variables for optimal performance
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
        
        # TF32 is enabled by default for compute capability >= 8.0 (A100, H100)
        # Explicitly enable for clarity
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        
        # Set to benchmark for optimized performance once shapes are stable
        torch.backends.cudnn.benchmark = True
        
        # Use deterministic algorithms only if explicitly requested for reproducibility
        if not os.getenv("DETERMINISTIC", "0") == "1":
            torch.backends.cudnn.deterministic = False
        
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        self.logger.info(f"Using GPU: {gpu_name} with {gpu_memory:.2f} GB memory")
        
        # Check if it's an H100
        self.is_h100 = "H100" in gpu_name
        if self.is_h100:
            self.logger.info("H100 GPU detected - optimal performance expected")
        
    def get_gpu_memory_info(self):
        """Get current GPU memory usage"""
        if not torch.cuda.is_available():
            return "CUDA not available"
        
        result = {}
        for i in range(torch.cuda.device_count()):
            gpu_memory = torch.cuda.get_device_properties(i).total_memory
            gpu_memory_allocated = torch.cuda.memory_allocated(i)
            gpu_memory_reserved = torch.cuda.memory_reserved(i)
            
            result[f"gpu_{i}"] = {
                "total": gpu_memory / 1024**3,
                "allocated": gpu_memory_allocated / 1024**3,
                "reserved": gpu_memory_reserved / 1024**3,
                "free": (gpu_memory - gpu_memory_reserved) / 1024**3
            }
        
        return result
        
    def clear_gpu_memory(self):
        """Clear GPU memory cache"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            import gc
            gc.collect()
            self.logger.info("GPU memory cache cleared")
    
    def generate_video(self, prompt, output_path, width=1280, height=720, 
                      video_length=129, steps=50, seed=None, guidance_scale=6.0, 
                      flow_shift=7.0, flow_reverse=True, use_fp8=True, multi_gpu=False):
        """
        Generate a video from a text prompt
        
        Args:
            prompt: Text prompt describing the video to generate
            output_path: Path where the video will be saved
            width: Video width
            height: Video height
            video_length: Number of frames
            steps: Number of inference steps
            seed: Random seed for reproducibility
            guidance_scale: Classifier-free guidance scale
            flow_shift: Flow shift parameter
            flow_reverse: Whether to use flow reversal
            use_fp8: Whether to use FP8 precision for memory efficiency
            multi_gpu: Whether to use multiple GPUs (Ulysses parallelism)
            
        Returns:
            Path to the generated video
        """
        try:
            start_time = time.time()
            self.logger.info(f"Starting generation for prompt: {prompt}")
            
            # Apply optimizations for high resolution
            is_high_res = width >= 1920 or height >= 1080
            
            # For high res, ensure we're using FP8 to save memory
            if is_high_res and not use_fp8 and self.fp8_weights_path:
                self.logger.warning("High resolution detected. Enabling FP8 for memory efficiency.")
                use_fp8 = True
            
            # For high res, reduce steps if too high to conserve memory
            if is_high_res and steps > 40:
                self.logger.warning(f"High resolution with high step count ({steps}). Reducing to 40 steps.")
                steps = 40
            
            # For high res on H100, use multi-GPU if available
            gpu_count = torch.cuda.device_count()
            if is_high_res and not multi_gpu and gpu_count > 1 and self.is_h100:
                self.logger.info("High resolution with multiple GPUs available. Enabling multi-GPU inference.")
                multi_gpu = True
            
            # Build command based on configuration
            if multi_gpu and gpu_count > 1:
                # Multi-GPU inference using Ulysses parallelism
                cmd = [
                    "torchrun", 
                    f"--nproc_per_node={gpu_count}",
                    "sample_video.py",
                    "--video-size", str(width), str(height),
                    "--video-length", str(video_length),
                    "--infer-steps", str(steps),
                    "--prompt", prompt,
                    "--embedded-cfg-scale", str(guidance_scale),
                    "--flow-shift", str(flow_shift),
                    "--ulysses-degree", str(gpu_count),
                    "--ring-degree", "1",
                    "--save-path", output_path
                ]
            else:
                # Single-GPU inference 
                cmd = [
                    "python3", "sample_video.py",
                    "--video-size", str(width), str(height),
                    "--video-length", str(video_length),
                    "--infer-steps", str(steps),
                    "--prompt", prompt,
                    "--embedded-cfg-scale", str(guidance_scale),
                    "--flow-shift", str(flow_shift),
                    "--save-path", output_path
                ]
                
                # Use FP8 weights if specified for reduced memory usage
                if use_fp8 and self.fp8_weights_path:
                    cmd.extend(["--dit-weight", self.fp8_weights_path, "--use-fp8"])
            
            # Set seed if provided
            if seed is not None:
                cmd.extend(["--seed", str(seed)])
                
            # Add flow reverse flag if needed
            if flow_reverse:
                cmd.append("--flow-reverse")
                
            # Log memory usage before running
            self.logger.info(f"GPU memory before generation: {self.get_gpu_memory_info()}")
            
            # Run the command
            self.logger.info(f"Running command: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Video generation failed: {stderr}")
                raise Exception(f"Video generation failed: {stderr}")
            
            generation_time = time.time() - start_time
            self.logger.info(f"Video generated successfully at {output_path}")
            self.logger.info(f"Generation took {generation_time:.2f} seconds")
            
            # Log memory usage after running
            self.logger.info(f"GPU memory after generation: {self.get_gpu_memory_info()}")
            
            # Clear GPU memory after generation
            self.clear_gpu_memory()
            
            return {
                "path": output_path,
                "generation_time": generation_time,
                "success": True
            }
        
        except Exception as e:
            self.logger.error(f"Error in video generation: {str(e)}")
            self.clear_gpu_memory()
            return {
                "success": False,
                "error": str(e)
            } 
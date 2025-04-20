#!/usr/bin/env python3
import os
import argparse
import time
import torch
import logging
from pathlib import Path
import subprocess
from dotenv import load_dotenv
import gc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HunyuanVideo-Optimizer")

# Load environment variables
load_dotenv()

# Get the model path from environment variable or use default
MODEL_PATH = os.getenv("HUNYUANVIDEO_MODEL_PATH", "/root/.cache/huggingface/hub")
RESULTS_DIR = os.getenv("RESULTS_DIR", "./results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def optimize_cuda_settings():
    """Apply CUDA optimizations specifically for H100 GPUs"""
    # Set CUDA related environment variables for optimal performance
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
    os.environ["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "0")
    
    # TF32 is enabled by default for compute capability >= 8.0 (A100, H100)
    # Explicitly enable for clarity
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    
    # Set to benchmark for optimized performance once shapes are stable
    torch.backends.cudnn.benchmark = True
    
    # Use deterministic algorithms only if explicitly requested for reproducibility
    if not os.getenv("DETERMINISTIC", "0") == "1":
        torch.backends.cudnn.deterministic = False
    
    logger.info("CUDA settings optimized for H100")

def get_gpu_memory_info():
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

def clear_gpu_memory():
    """Clear GPU memory cache"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        gc.collect()
        logger.info("GPU memory cache cleared")

def run_video_generation(
    prompt,
    output_path,
    width=1280,
    height=720,
    video_length=129,
    steps=50,
    seed=None,
    embedded_cfg_scale=6.0,
    flow_shift=7.0,
    flow_reverse=True,
    use_fp8=True,
    fp8_weights_path=None,
    use_ulysses=False,
    ulysses_degree=1,
    ring_degree=1,
    gpu_count=1
):
    """Run HunyuanVideo video generation with optimized parameters"""
    try:
        start_time = time.time()
        logger.info(f"Starting generation for prompt: {prompt}")
        
        # Apply optimizations for 1080p generation
        is_high_res = width >= 1920 or height >= 1080
        
        # For 1080p, ensure we're using FP8 to save memory
        if is_high_res and not use_fp8:
            logger.warning("High resolution detected (1080p+). Enabling FP8 for memory efficiency.")
            use_fp8 = True
        
        # For 1080p, reduce steps if too high to conserve memory
        if is_high_res and steps > 40:
            logger.warning(f"High resolution detected with high step count ({steps}). Reducing to 40 steps for stability.")
            steps = 40
        
        # For 1080p, use multi-GPU if available
        if is_high_res and gpu_count == 1 and torch.cuda.device_count() > 1:
            logger.warning("High resolution detected with multiple GPUs available. Enabling multi-GPU inference.")
            use_ulysses = True
            gpu_count = torch.cuda.device_count()
            ulysses_degree = gpu_count
            ring_degree = 1
        
        # Build command based on configuration
        if use_ulysses and gpu_count > 1:
            # Multi-GPU inference using Ulysses parallelism
            cmd = [
                "torchrun", 
                f"--nproc_per_node={gpu_count}",
                "sample_video.py",
                "--video-size", str(width), str(height),
                "--video-length", str(video_length),
                "--infer-steps", str(steps),
                "--prompt", prompt,
                "--embedded-cfg-scale", str(embedded_cfg_scale),
                "--flow-shift", str(flow_shift),
                "--ulysses-degree", str(ulysses_degree),
                "--ring-degree", str(ring_degree),
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
                "--embedded-cfg-scale", str(embedded_cfg_scale),
                "--flow-shift", str(flow_shift),
                "--save-path", output_path
            ]
            
            # Use FP8 weights if specified for reduced memory usage
            if use_fp8 and fp8_weights_path:
                cmd.extend(["--dit-weight", fp8_weights_path, "--use-fp8"])
        
        # Set seed if provided
        if seed is not None:
            cmd.extend(["--seed", str(seed)])
            
        # Add flow reverse flag if needed
        if flow_reverse:
            cmd.append("--flow-reverse")
            
        # Print memory usage before running
        logger.info(f"GPU memory before generation: {get_gpu_memory_info()}")
        
        # Run the command
        logger.info(f"Running command: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Video generation failed: {stderr}")
            raise Exception(f"Video generation failed: {stderr}")
        
        logger.info(f"Video generated successfully at {output_path}")
        logger.info(f"Generation took {time.time() - start_time:.2f} seconds")
        
        # Print memory usage after running
        logger.info(f"GPU memory after generation: {get_gpu_memory_info()}")
        
        # Clear GPU memory after generation
        clear_gpu_memory()
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error in video generation: {str(e)}")
        raise e

def batch_generate(
    prompts, 
    output_dir=RESULTS_DIR, 
    **kwargs
):
    """Generate multiple videos in sequence with optimized memory management"""
    results = []
    
    for i, prompt in enumerate(prompts):
        logger.info(f"Processing prompt {i+1}/{len(prompts)}")
        
        # Create unique output path
        timestamp = int(time.time())
        output_file = f"video_{timestamp}_{i}.mp4"
        output_path = os.path.join(output_dir, output_file)
        
        try:
            # Generate the video
            video_path = run_video_generation(
                prompt=prompt,
                output_path=output_path,
                **kwargs
            )
            
            results.append({
                "prompt": prompt,
                "path": video_path,
                "success": True
            })
            
            # Clear memory after each generation
            clear_gpu_memory()
            
        except Exception as e:
            logger.error(f"Failed to generate video for prompt: {prompt}")
            logger.error(f"Error: {str(e)}")
            
            results.append({
                "prompt": prompt,
                "error": str(e),
                "success": False
            })
            
            # Make sure to clean up memory after errors
            clear_gpu_memory()
    
    return results

# Add supported resolutions and their configurations
SUPPORTED_RESOLUTIONS = {
    # Full HD - for high quality videos
    (1920, 1080): {
        "recommended_steps": 40,
        "recommended_gpu_memory": 60, # GB
        "min_gpu_memory": 40, # GB
        "use_fp8": True,
        "multi_gpu_recommended": True
    },
    # HD - good balance of quality and speed
    (1280, 720): {
        "recommended_steps": 50,
        "recommended_gpu_memory": 32, # GB
        "min_gpu_memory": 24, # GB
        "use_fp8": True,
        "multi_gpu_recommended": False
    },
    # SD - faster generation
    (960, 544): {
        "recommended_steps": 50,
        "recommended_gpu_memory": 24, # GB
        "min_gpu_memory": 16, # GB
        "use_fp8": False,
        "multi_gpu_recommended": False
    },
    # Square - optimized for social media
    (720, 720): {
        "recommended_steps": 50,
        "recommended_gpu_memory": 24, # GB
        "min_gpu_memory": 16, # GB
        "use_fp8": False,
        "multi_gpu_recommended": False
    }
}

def check_resolution_support(width, height):
    """Check if a resolution is supported and get optimal settings"""
    resolution = (width, height)
    
    if resolution in SUPPORTED_RESOLUTIONS:
        # Get recommended settings
        settings = SUPPORTED_RESOLUTIONS[resolution]
        
        # Check available GPU memory
        if torch.cuda.is_available():
            total_memory = 0
            for i in range(torch.cuda.device_count()):
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                total_memory += gpu_memory
            
            if total_memory < settings["min_gpu_memory"]:
                return {
                    "supported": False,
                    "reason": f"Not enough GPU memory. Required: {settings['min_gpu_memory']}GB, Available: {total_memory:.1f}GB"
                }
        
        return {
            "supported": True,
            "settings": settings
        }
    else:
        # Find closest supported resolution
        closest = None
        closest_area_diff = float('inf')
        target_area = width * height
        
        for res in SUPPORTED_RESOLUTIONS:
            res_width, res_height = res
            res_area = res_width * res_height
            area_diff = abs(res_area - target_area)
            
            if area_diff < closest_area_diff:
                closest = res
                closest_area_diff = area_diff
        
        closest_width, closest_height = closest
        return {
            "supported": False,
            "reason": f"Unsupported resolution: {width}x{height}",
            "recommendation": f"Use {closest_width}x{closest_height} instead"
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimized HunyuanVideo Generator for H100 GPUs")
    
    # Input parameters
    parser.add_argument("--prompt", type=str, help="Text prompt for video generation")
    parser.add_argument("--prompts-file", type=str, help="File containing prompts, one per line")
    
    # Video configuration
    parser.add_argument("--width", type=int, default=1280, help="Video width")
    parser.add_argument("--height", type=int, default=720, help="Video height")
    parser.add_argument("--video-length", type=int, default=129, help="Number of frames")
    parser.add_argument("--steps", type=int, default=50, help="Number of inference steps")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--embedded-cfg-scale", type=float, default=6.0, help="Classifier free guidance scale")
    parser.add_argument("--flow-shift", type=float, default=7.0, help="Flow shift value")
    parser.add_argument("--flow-reverse", action="store_true", help="Use flow reverse")
    
    # Performance optimization
    parser.add_argument("--use-fp8", action="store_true", help="Use FP8 precision for memory efficiency")
    parser.add_argument("--fp8-weights-path", type=str, help="Path to FP8 weights")
    parser.add_argument("--use-ulysses", action="store_true", help="Use Ulysses parallelism for multi-GPU")
    parser.add_argument("--ulysses-degree", type=int, default=1, help="Ulysses parallelism degree")
    parser.add_argument("--ring-degree", type=int, default=1, help="Ring parallelism degree")
    parser.add_argument("--gpu-count", type=int, default=1, help="Number of GPUs to use")
    
    # Output
    parser.add_argument("--output-dir", type=str, default=RESULTS_DIR, help="Output directory")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Apply CUDA optimizations
    optimize_cuda_settings()
    
    # Check resolution support
    resolution_check = check_resolution_support(args.width, args.height)
    if not resolution_check["supported"]:
        logger.warning(resolution_check["reason"])
        if "recommendation" in resolution_check:
            logger.warning(resolution_check["recommendation"])
    else:
        # Apply recommended settings if not explicitly overridden
        settings = resolution_check["settings"]
        if args.steps is None:
            args.steps = settings["recommended_steps"]
        if args.use_fp8 is None:
            args.use_fp8 = settings["use_fp8"]
        
        # Enable multi-GPU if recommended and available
        if settings["multi_gpu_recommended"] and torch.cuda.device_count() > 1 and not args.use_ulysses:
            logger.info(f"Enabling multi-GPU for resolution {args.width}x{args.height}")
            args.use_ulysses = True
            args.gpu_count = torch.cuda.device_count()
            args.ulysses_degree = args.gpu_count
    
    # Get prompts from file or command line
    prompts = []
    if args.prompts_file:
        with open(args.prompts_file, 'r') as f:
            prompts = [line.strip() for line in f if line.strip()]
    elif args.prompt:
        prompts = [args.prompt]
    else:
        parser.error("Either --prompt or --prompts-file must be provided")
    
    logger.info(f"Starting batch generation for {len(prompts)} prompts")
    
    # Generate videos
    results = batch_generate(
        prompts=prompts,
        output_dir=args.output_dir,
        width=args.width,
        height=args.height,
        video_length=args.video_length,
        steps=args.steps,
        seed=args.seed,
        embedded_cfg_scale=args.embedded_cfg_scale,
        flow_shift=args.flow_shift,
        flow_reverse=args.flow_reverse,
        use_fp8=args.use_fp8,
        fp8_weights_path=args.fp8_weights_path,
        use_ulysses=args.use_ulysses,
        ulysses_degree=args.ulysses_degree,
        ring_degree=args.ring_degree,
        gpu_count=args.gpu_count
    )
    
    # Print results summary
    success_count = sum(1 for r in results if r["success"])
    logger.info(f"Generation complete: {success_count}/{len(results)} videos generated successfully")
    
    for i, result in enumerate(results):
        if result["success"]:
            logger.info(f"Video {i+1}: {result['path']}")
        else:
            logger.error(f"Video {i+1} failed: {result['error']}") 
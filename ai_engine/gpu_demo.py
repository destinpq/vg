import os
import asyncio
import time
import sys
from pathlib import Path
import torch

# Add parent directory to path to fix imports
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Use direct imports rather than package-based imports
from mochi_wrapper import MochiWrapper

async def generate_demo_video():
    """
    Generate a demo video using the GPU-accelerated Mochi wrapper
    """
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Display GPU information
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        memory_info = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # Convert to GB
        print(f"\n--- Using GPU: {gpu_name} with {memory_info:.2f} GB memory ---\n")
    else:
        print("\n--- GPU not available, using CPU (much slower) ---\n")
    
    # Initialize the Mochi wrapper (this will automatically use GPU if available)
    mochi = MochiWrapper()
    
    # Define sample prompts that would benefit from GPU processing
    prompts = [
        "A spaceship flying through a nebula, cinematic 4K",
        "Timelapse of a blooming flower with dew drops, high resolution",
        "Drone flyover of a mountain range at sunset, cinematic",
        "Dolphins jumping out of crystal clear water, slow motion",
        "A futuristic city with flying cars and neon lights, rainy night"
    ]
    
    # Generate videos for each prompt with performance metrics
    for i, prompt in enumerate(prompts):
        output_path = output_dir / f"gpu_demo_{i+1}.mp4"
        
        print(f"\nGenerating video {i+1}/5: '{prompt}'")
        
        # Measure generation time
        start_time = time.time()
        
        # Generate the video
        await mochi.generate_video(
            prompt=prompt,
            output_path=output_path,
            duration=5.0,
            fps=24,
            num_inference_steps=50,
            guidance_scale=7.5
        )
        
        # Calculate and display performance metrics
        end_time = time.time()
        generation_time = end_time - start_time
        fps = (5.0 * 24) / generation_time  # 5 seconds of video at 24fps
        
        print(f"Video generated at: {output_path}")
        print(f"Generation time: {generation_time:.2f} seconds")
        print(f"Effective speed: {fps:.2f} frames per second")
        
        # Clear any remaining GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    print("\n--- GPU Demo Completed ---")
    print(f"All videos have been saved to the '{output_dir}' directory")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(generate_demo_video()) 
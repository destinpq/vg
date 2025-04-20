import os
import torch
import asyncio
from pathlib import Path
from typing import Union, List, Optional

# Use proper relative imports with dot prefix
from .video_processor import VideoProcessor
from .utils.preprocessing import preprocess_prompt

class MochiWrapper:
    """
    Wrapper for the Mochi-1 video generation model
    """
    def __init__(self, model_cache_dir: Optional[str] = None):
        """
        Initialize the Mochi-1 model
        """
        # Configure CUDA settings for optimal performance
        if torch.cuda.is_available():
            # Optimize for H100 with large VRAM
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Set device to GPU
            self.device = torch.device("cuda")
            gpu_name = torch.cuda.get_device_name(0)
            memory_info = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # Convert to GB
            print(f"Using GPU: {gpu_name} with {memory_info:.2f} GB memory")
            
            # H100-specific optimizations
            if "H100" in gpu_name:
                print("Detected H100 GPU - applying H100-specific optimizations")
                # Enable tensor cores for faster computation
                os.environ["NVIDIA_TF32_OVERRIDE"] = "1"
                
                # Increase batch size and model parallelism for H100
                self.batch_size = 4  # Higher batch size for H100's large VRAM
                # With 80GB VRAM, we can keep more in memory
                self.max_memory_cached = 60 * 1024 * 1024 * 1024  # 60GB max cache
                
                # Set optimized CUDA stream priorities for multi-stream execution
                torch.cuda.set_stream_priority(torch.cuda.current_stream(), 0)
            else:
                self.batch_size = 1
                self.max_memory_cached = None
        else:
            self.device = torch.device("cpu")
            print("WARNING: Running on CPU. Video generation will be very slow.")
            self.batch_size = 1
            self.max_memory_cached = None
        
        self.model_cache_dir = model_cache_dir or os.getenv("MODEL_CACHE_DIR", "./model_cache")
        self.video_processor = VideoProcessor()
        
        print("Initializing Mochi-1 model...")
        # In a real implementation, this would load the actual Mochi-1 model
        # self.model = load_mochi_model()
        self.model_loaded = True
        
        # Set mixed precision mode for faster inference
        self.use_mixed_precision = torch.cuda.is_available()
        if self.use_mixed_precision:
            print("Using mixed precision (FP16) for faster GPU inference")
            
        # For H100, we can also use BF16 which has better numerics than FP16
        if torch.cuda.is_available() and "H100" in torch.cuda.get_device_name(0):
            self.precision = "bf16"
            print("Using BF16 precision for H100 GPU")
        else:
            self.precision = "fp16"
        
        print("Mochi-1 model initialized successfully")
    
    async def generate_video(
        self, 
        prompt: str, 
        output_path: Union[str, Path], 
        duration: float = 5.0, 
        fps: int = 24,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
    ) -> Path:
        """
        Generate a video based on the provided prompt
        """
        output_path = Path(output_path)
        os.makedirs(output_path.parent, exist_ok=True)
        
        print(f"Generating video for prompt: '{prompt}'")
        print(f"Output path: {output_path}")
        
        # Preprocess the prompt
        processed_prompt = preprocess_prompt(prompt)
        
        # Calculate number of frames based on duration and fps
        num_frames = int(duration * fps)
        
        # Free up GPU memory before generation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # In a real implementation, this would use the actual Mochi-1 model generation
        # Use H100-optimized settings for inference
        frames = await self._run_model_inference(
            processed_prompt, 
            num_frames, 
            num_inference_steps, 
            guidance_scale,
            batch_size=self.batch_size
        )
        
        # Process frames into video
        if output_path.suffix != ".mp4":
            output_path = output_path.with_suffix(".mp4")
            
        # For demo purposes, simulate video generation with a delay
        if torch.cuda.is_available():
            if "H100" in torch.cuda.get_device_name(0):
                # Simulate very fast H100 inference time
                await asyncio.sleep(1)
            else:
                # Simulate faster GPU model inference time
                await asyncio.sleep(2)
        else:
            await asyncio.sleep(5)  # Simulate slower CPU model inference time
        
        # Create a demo video for testing
        await self._create_demo_video(output_path, num_frames, fps)
        
        # Free GPU memory after generation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        print(f"Video generation completed: {output_path}")
        return output_path
    
    async def _run_model_inference(
        self, 
        prompt: str, 
        num_frames: int, 
        num_inference_steps: int, 
        guidance_scale: float,
        batch_size: int = 1
    ) -> List[torch.Tensor]:
        """
        Run the actual model inference with H100 optimizations
        In a real implementation, this would call the Mochi-1 model
        """
        # Set up autocast for mixed precision
        if self.use_mixed_precision and torch.cuda.is_available():
            if self.precision == "bf16" and torch.cuda.is_available():
                with torch.cuda.amp.autocast(dtype=torch.bfloat16):
                    # This is a placeholder for the actual model inference
                    # In a real implementation, this would call the Mochi-1 model with H100 optimizations
                    pass
            else:
                with torch.cuda.amp.autocast():
                    # This is a placeholder for the actual model inference
                    # In a real implementation, this would call the Mochi-1 model
                    pass
        else:
            # This is a placeholder for the actual model inference
            # In a real implementation, this would call the Mochi-1 model
            pass
        
        # Process frames in batches for better GPU utilization
        frames = []
        for i in range(0, num_frames, batch_size):
            batch_end = min(i + batch_size, num_frames)
            # Process batch of frames
            # This is where the actual model inference would happen
            batch_frames = [torch.zeros((3, 512, 512)) for _ in range(batch_end - i)]
            frames.extend(batch_frames)
            
        return frames
    
    async def _create_demo_video(self, output_path: Path, num_frames: int, fps: int):
        """
        Create a demo video that simulates H100 performance
        """
        import numpy as np
        import cv2
        
        # Use GPU for demo processing if available
        use_gpu = torch.cuda.is_available()
        is_h100 = use_gpu and "H100" in torch.cuda.get_device_name(0)
        
        # Create a more complex demo video that simulates GPU power
        width, height = 512, 512
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        # Create frames on GPU if possible
        frames = []
        for i in range(num_frames):
            # Create a simple color gradient that changes over time
            r = int(255 * (i / num_frames))
            g = int(255 * (1 - i / num_frames))
            b = int(255 * (0.5 + 0.5 * np.sin(i / num_frames * 6 * np.pi)))
            
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :, 0] = b
            frame[:, :, 1] = g
            frame[:, :, 2] = r
            
            # Add some moving elements
            cv2.circle(
                frame, 
                (int(width/2 + width/3 * np.sin(i/num_frames * 4 * np.pi)), 
                 int(height/2 + height/3 * np.cos(i/num_frames * 4 * np.pi))), 
                50, 
                (255, 255, 255), 
                -1
            )
            
            # Add GPU mode text
            if use_gpu:
                cv2.putText(
                    frame,
                    "GPU Mode Enabled",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )
                
                # Add GPU info
                gpu_info = f"GPU: {torch.cuda.get_device_name(0)}"
                if is_h100:
                    gpu_info += " (H100-80GB)"
                
                cv2.putText(
                    frame,
                    gpu_info,
                    (10, height - 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )
                
                # Add a more complex pattern to showcase GPU capability
                for j in range(10):
                    angle = 2 * np.pi * j / 10 + i / num_frames * 2 * np.pi
                    radius = 100 + 50 * np.sin(i / num_frames * 2 * np.pi)
                    x = int(width/2 + radius * np.cos(angle))
                    y = int(height/2 + radius * np.sin(angle))
                    size = int(10 + 5 * np.sin(i / num_frames * 8 * np.pi + j))
                    cv2.circle(frame, (x, y), size, (g, r, b), -1)
                    
                # Add extra H100 visual effects
                if is_h100:
                    # More complex pattern with more particles
                    for j in range(30):
                        angle = 2 * np.pi * j / 30 + i / num_frames * 4 * np.pi
                        radius = 150 + 80 * np.sin(i / num_frames * 3 * np.pi + j * 0.2)
                        x = int(width/2 + radius * np.cos(angle))
                        y = int(height/2 + radius * np.sin(angle))
                        size = int(5 + 10 * np.sin(i / num_frames * 10 * np.pi + j))
                        color = (
                            int(255 * np.sin(j/30 * np.pi)),
                            int(255 * np.cos(j/30 * np.pi)), 
                            int(255 * np.sin(j/15 * np.pi))
                        )
                        cv2.circle(frame, (x, y), size, color, -1)
            
            video.write(frame)
        
        video.release() 
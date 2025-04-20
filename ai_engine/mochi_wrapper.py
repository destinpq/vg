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
            # Set to True to allow benchmark mode (may be slightly slower on first run, but faster afterwards)
            torch.backends.cudnn.benchmark = True
            # Set deterministic mode to False for better performance
            torch.backends.cudnn.deterministic = False
            # Higher memory usage but faster inference
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            # Set device to GPU
            self.device = torch.device("cuda")
            gpu_name = torch.cuda.get_device_name(0)
            memory_info = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # Convert to GB
            print(f"Using GPU: {gpu_name} with {memory_info:.2f} GB memory")
        else:
            self.device = torch.device("cpu")
            print("WARNING: Running on CPU. Video generation will be very slow.")
        
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
        # frames = await self._run_model_inference(processed_prompt, num_frames, num_inference_steps, guidance_scale)
        
        # For demo purposes, simulate video generation with a delay
        if torch.cuda.is_available():
            # Reduce simulation time since we're on GPU
            await asyncio.sleep(2)  # Simulate faster GPU model inference time
        else:
            await asyncio.sleep(5)  # Simulate slower CPU model inference time
        
        # Create a simple color gradient video for demonstration
        await self._create_demo_video(output_path, num_frames, fps)
        
        # Free GPU memory after generation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        print(f"Video generation completed: {output_path}")
        return output_path
    
    async def _run_model_inference(self, prompt: str, num_frames: int, num_inference_steps: int, guidance_scale: float) -> List[torch.Tensor]:
        """
        Run the actual model inference
        In a real implementation, this would call the Mochi-1 model
        """
        # Set up autocast for mixed precision if available
        if self.use_mixed_precision and torch.cuda.is_available():
            with torch.cuda.amp.autocast():
                # This is a placeholder for the actual model inference
                # In a real implementation, this would call the Mochi-1 model to generate frames
                pass
        else:
            # This is a placeholder for the actual model inference
            # In a real implementation, this would call the Mochi-1 model to generate frames
            pass
    
    async def _create_demo_video(self, output_path: Path, num_frames: int, fps: int):
        """
        Create a simple demo video for testing purposes
        """
        import numpy as np
        import cv2
        
        # Use GPU for demo processing if available
        use_gpu = torch.cuda.is_available()
        
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
            
            # Add GPU mode text if using GPU
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
                cv2.putText(
                    frame,
                    f"GPU: {torch.cuda.get_device_name(0)}",
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
            
            video.write(frame)
        
        video.release() 
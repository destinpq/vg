import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model settings
MODEL_PATH = os.getenv("HUNYUANVIDEO_MODEL_PATH", "/root/.cache/huggingface/hub")
FP8_WEIGHTS_PATH = os.getenv("FP8_WEIGHTS_PATH")

# Output settings
RESULTS_DIR = os.getenv("RESULTS_DIR", "./results")

# Processing settings
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "1"))

# Video generation settings
DEFAULT_RESOLUTION = (1280, 720)
DEFAULT_VIDEO_LENGTH = 129
DEFAULT_STEPS = 50
DEFAULT_GUIDANCE_SCALE = 6.0
DEFAULT_FLOW_SHIFT = 7.0
DEFAULT_FLOW_REVERSE = True
DEFAULT_USE_FP8 = True

# Supported resolutions with their configurations
SUPPORTED_RESOLUTIONS = {
    # Full HD - for high quality videos
    (1920, 1080): {
        "name": "Full HD (1080p)",
        "quality": "High",
        "recommended_steps": 40,
        "recommended_gpu_memory": 60,  # GB
        "min_gpu_memory": 40,  # GB
        "use_fp8": True,
        "multi_gpu_recommended": True
    },
    # HD - good balance of quality and speed
    (1280, 720): {
        "name": "HD (720p)",
        "quality": "Good",
        "recommended_steps": 50,
        "recommended_gpu_memory": 32,  # GB
        "min_gpu_memory": 24,  # GB
        "use_fp8": True,
        "multi_gpu_recommended": False
    },
    # SD - faster generation
    (960, 544): {
        "name": "SD (544p)",
        "quality": "Medium",
        "recommended_steps": 50,
        "recommended_gpu_memory": 24,  # GB
        "min_gpu_memory": 16,  # GB
        "use_fp8": False,
        "multi_gpu_recommended": False
    },
    # Square - optimized for social media
    (720, 720): {
        "name": "Square",
        "quality": "Good",
        "recommended_steps": 50,
        "recommended_gpu_memory": 24,  # GB
        "min_gpu_memory": 16,  # GB
        "use_fp8": False,
        "multi_gpu_recommended": False
    }
} 
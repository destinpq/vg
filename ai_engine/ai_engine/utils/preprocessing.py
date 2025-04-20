import re
from typing import Dict, Any, Optional

def preprocess_prompt(prompt: str) -> str:
    """
    Preprocess the user prompt for better video generation results
    
    Args:
        prompt: The raw user input prompt
        
    Returns:
        Processed prompt ready for the model
    """
    # Remove extra whitespace
    prompt = prompt.strip()
    prompt = re.sub(r'\s+', ' ', prompt)
    
    # Add video-specific enhancers if not present
    video_keywords = ["cinematic", "dynamic", "motion", "scene", "video"]
    has_video_keyword = any(keyword.lower() in prompt.lower() for keyword in video_keywords)
    
    if not has_video_keyword:
        prompt = f"cinematic video of {prompt}"
    
    # Add quality enhancers if not present
    quality_keywords = ["high quality", "detailed", "4k", "hd", "sharp"]
    has_quality_keyword = any(keyword.lower() in prompt.lower() for keyword in quality_keywords)
    
    if not has_quality_keyword:
        prompt = f"{prompt}, high quality, detailed"
    
    return prompt

def extract_prompt_attributes(prompt: str) -> Dict[str, Any]:
    """
    Extract various attributes from the prompt for more targeted generation
    
    Args:
        prompt: The user input prompt
        
    Returns:
        Dictionary of prompt attributes
    """
    attributes = {
        "style": None,
        "lighting": None,
        "camera_movement": None,
        "subjects": [],
        "environment": None,
        "time_of_day": None,
    }
    
    # Extract style
    style_patterns = [
        r'(cinematic|anime|cartoon|photorealistic|3d|abstract|noir|vintage)',
        r'in the style of (\w+)',
    ]
    for pattern in style_patterns:
        style_match = re.search(pattern, prompt, re.IGNORECASE)
        if style_match:
            attributes["style"] = style_match.group(1).lower()
            break
    
    # Extract lighting
    lighting_patterns = [
        r'(bright|dark|soft|harsh|natural|neon|ambient) lighting',
        r'(sunlight|moonlight|candlelight|firelight)',
    ]
    for pattern in lighting_patterns:
        lighting_match = re.search(pattern, prompt, re.IGNORECASE)
        if lighting_match:
            attributes["lighting"] = lighting_match.group(1).lower()
            break
    
    # Extract camera movement
    camera_patterns = [
        r'(panning|zooming|tracking|aerial|dolly|handheld|static) (shot|camera|view)',
    ]
    for pattern in camera_patterns:
        camera_match = re.search(pattern, prompt, re.IGNORECASE)
        if camera_match:
            attributes["camera_movement"] = camera_match.group(1).lower()
            break
    
    # Extract time of day
    time_patterns = [
        r'(morning|afternoon|evening|night|dawn|dusk|sunset|sunrise)',
    ]
    for pattern in time_patterns:
        time_match = re.search(pattern, prompt, re.IGNORECASE)
        if time_match:
            attributes["time_of_day"] = time_match.group(1).lower()
            break
    
    return attributes

def optimize_prompt_for_resolution(prompt: str, width: int, height: int) -> str:
    """
    Optimize a prompt for specific resolution
    
    Args:
        prompt: Original text prompt
        width: Video width
        height: Video height
        
    Returns:
        Optimized prompt
    """
    # Add resolution-specific terms
    is_high_res = width >= 1920 or height >= 1080
    is_square = abs(width - height) < 100
    
    if is_high_res:
        # For high-res, emphasize detail and quality
        if "4k" not in prompt.lower() and "hd" not in prompt.lower():
            prompt = f"{prompt}, 4K resolution, highly detailed"
    
    if is_square:
        # For square videos, consider composition
        if "centered composition" not in prompt.lower():
            prompt = f"{prompt}, centered composition"
    
    return prompt 
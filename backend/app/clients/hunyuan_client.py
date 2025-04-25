"""
Hunyuan API client for backwards compatibility.

This module forwards to the hunyuan_service for MVC structure compatibility.
"""
import logging
from pathlib import Path
from typing import Dict, Any

from ..services.hunyuan_service import hunyuan_service

# Configure logging
logger = logging.getLogger(__name__)

class HunyuanClient:
    """Client for communicating with the Hunyuan API (forwarding to service)."""
    
    def __init__(self, api_url=None):
        """Initialize the client."""
        # We'll use hunyuan_service instead, just store the URL
        self.api_url = api_url or hunyuan_service.api_url
        self.health_url = hunyuan_service.health_url
        self.generate_url = hunyuan_service.generate_url
    
    def check_health(self) -> Dict[str, Any]:
        """Check if the Hunyuan API is healthy (wrapper for backward compatibility)."""
        # Use asyncio.run to call the async method
        import asyncio
        
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run the async function in the loop
            return loop.run_until_complete(hunyuan_service.check_health())
        finally:
            # Close the loop
            loop.close()
    
    def generate_video(self, prompt, num_inference_steps=50, height=320, width=576, output_format="gif") -> Dict[str, Any]:
        """Generate a video using the Hunyuan API (wrapper for backward compatibility)."""
        # Use asyncio.run to call the async method
        import asyncio
        
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run the async function in the loop
            return loop.run_until_complete(
                hunyuan_service.generate_video(
                    prompt=prompt,
                    num_inference_steps=num_inference_steps,
                    height=height,
                    width=width,
                    output_format=output_format
                )
            )
        finally:
            # Close the loop
            loop.close()

# Create singleton instance
hunyuan_client = HunyuanClient() 